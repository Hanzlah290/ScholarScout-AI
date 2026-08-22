from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Set
import uuid

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.source import Source
from app.services.automation.discovery import SourceDiscoveryEngine

logger = logging.getLogger(__name__)


class AutomationManager:
    """Coordinates source scheduling, concurrency locking, and failure backoff."""

    # In-memory lock set preventing duplicate concurrent runs on the same source
    _active_locks: Set[uuid.UUID] = set()
    _lock_guard = asyncio.Lock()

    def __init__(self, discovery_engine: SourceDiscoveryEngine | None = None) -> None:
        self.discovery_engine = discovery_engine or SourceDiscoveryEngine()

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
        """
        Fetch all active sources where next_check_at is due (<= NOW()) or unassigned.
        Follows rule: 'Every 6 hours, ask PostgreSQL what work is due.'
        """
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

        # Calculate retry backoff based on failure count
        if source.consecutive_failures >= 3:
            source.status = "failing"
            # Exponential backoff: 24 hours after 3+ consecutive failures
            retry_delay = timedelta(hours=24)
        else:
            # Short retry backoff: 2 hours for transient issues
            retry_delay = timedelta(hours=2)

        source.next_check_at = now + retry_delay

        db.add(source)
        db.commit()
        db.refresh(source)
        logger.warning(
            f"[AUTOMATION MANAGER] Source '{source.name}' failed ({error_message}). "
            f"Failures: {source.consecutive_failures}. Retry scheduled for {source.next_check_at}."
        )

    async def run_discovery_cycle(self, db: Session) -> List[Source]:
        """Trigger source discovery to seed new candidate institutions into PostgreSQL."""
        logger.info("[AUTOMATION MANAGER] Running discovery cycle...")
        return await self.discovery_engine.run_discovery(db)