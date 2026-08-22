from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Set
import uuid

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.source import Source
from app.services.automation.discovery import SourceDiscoveryEngine
from app.services.collector.filesystem import RawDataCollector
from app.services.connectors.university import UniversitySourceConnector
from app.services.duplicate_checker.repository import ScholarshipDuplicateChecker
from app.services.extraction.openai_extractor import GeminiScholarshipExtractor
from app.services.filters.scholarship import ScholarshipPageFilter
from app.services.pipeline import ScholarshipDiscoveryPipeline
from app.services.validator.scholarship import ScholarshipValidator

logger = logging.getLogger(__name__)


class AutomationManager:
    """Coordinates source scheduling, concurrency locking, and failure backoff."""

    _active_locks: Set[uuid.UUID] = set()
    _lock_guard = asyncio.Lock()

    def __init__(
        self,
        discovery_engine: SourceDiscoveryEngine | None = None,
        pipeline: ScholarshipDiscoveryPipeline | None = None,
    ) -> None:
        self.discovery_engine = discovery_engine or SourceDiscoveryEngine()
        self.pipeline = pipeline or ScholarshipDiscoveryPipeline(
            connector=UniversitySourceConnector(),
            page_filter=ScholarshipPageFilter(),
            collector=RawDataCollector("storage/raw_pages"),
            extractor=GeminiScholarshipExtractor(),
            validator=ScholarshipValidator(),
            duplicate_checker=ScholarshipDuplicateChecker(),
        )

    @classmethod
    async def acquire_source_lock(cls, source_id: uuid.UUID) -> bool:
        """Attempt to acquire an in-process lock for a specific source."""
        async with cls._lock_guard:
            if source_id in cls._active_locks:
                return False
            cls._active_locks.add(source_id)
            return True

    @classmethod
    async def release_source_lock(cls, source_id: uuid.UUID) -> None:
        """Release the in-process lock for a source after processing."""
        async with cls._lock_guard:
            cls._active_locks.discard(source_id)

    @staticmethod
    def get_due_sources(db: Session) -> List[Source]:
        """Fetch all active sources where next_check_at is due (<= NOW()) or unassigned."""
        now = datetime.now(timezone.utc)
        return (
            db.query(Source)
            .filter(
                Source.enabled == True,
                Source.status != "disabled",
                or_(
                    Source.next_check_at <= now,
                    Source.next_check_at.is_(None)
                )
            )
            .all()
        )

    @staticmethod
    def record_success(db: Session, source: Source) -> None:
        """Update source timestamps after a successful pipeline run (+7 days cooldown)."""
        now = datetime.now(timezone.utc)
        source.last_checked_at = now
        source.last_success_at = now
        source.last_run_status = "success"
        source.consecutive_failures = 0
        source.status = "active"
        source.next_check_at = now + timedelta(days=7)
        
        db.add(source)
        db.commit()
        db.refresh(source)
        logger.info(f"[AUTOMATION MANAGER] Source '{source.name}' succeeded. Next check scheduled for {source.next_check_at}.")

    @staticmethod
    def record_failure(db: Session, source: Source, error_message: str) -> None:
        """Update source status and apply retry backoff on pipeline failure."""
        now = datetime.now(timezone.utc)
        source.last_checked_at = now
        source.last_failure_at = now
        source.last_run_status = "failed"
        source.consecutive_failures += 1

        if source.consecutive_failures >= 3:
            source.status = "failing"
            retry_delay = timedelta(hours=24)
        else:
            retry_delay = timedelta(hours=2)

        source.next_check_at = now + retry_delay

        db.add(source)
        db.commit()
        db.refresh(source)
        logger.warning(
            f"[AUTOMATION MANAGER] Source '{source.name}' failed ({error_message}). "
            f"Failures: {source.consecutive_failures}. Retry scheduled for {source.next_check_at}."
        )

    async def process_source(self, db: Session, source: Source) -> bool:
        """Process a single source through the scholarship discovery pipeline safely with locking."""
        locked = await self.acquire_source_lock(source.id)
        if not locked:
            logger.info(f"[AUTOMATION MANAGER] Skipping '{source.name}' - already processing under active lock.")
            return False

        try:
            logger.info(f"[AUTOMATION MANAGER] Executing pipeline for '{source.name}'...")
            await self.pipeline.run(db, source)
            self.record_success(db, source)
            return True
        except Exception as exc:
            logger.error(f"[AUTOMATION MANAGER] Pipeline execution failed for '{source.name}': {exc}")
            self.record_failure(db, source, str(exc))
            return False
        finally:
            await self.release_source_lock(source.id)

    async def process_due_sources(self, db: Session) -> int:
        """Fetch all due sources and execute their pipeline runs sequentially."""
        due_sources = self.get_due_sources(db)
        logger.info(f"[AUTOMATION MANAGER] Found {len(due_sources)} due sources for processing.")
        
        processed_count = 0
        for src in due_sources:
            success = await self.process_source(db, src)
            if success:
                processed_count += 1
                
        return processed_count

    async def run_discovery_cycle(self, db: Session) -> List[Source]:
        """Trigger source discovery to seed new candidate institutions into PostgreSQL."""
        logger.info("[AUTOMATION MANAGER] Running discovery cycle...")
        return await self.discovery_engine.run_discovery(db)