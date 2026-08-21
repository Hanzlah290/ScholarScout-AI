from __future__ import annotations

from threading import Lock

from sqlalchemy import select

from app.config.settings import settings
from app.database.session import SessionLocal
from app.models.source import Source
from app.services.collector.filesystem import RawDataCollector
from app.services.connectors.university import UniversitySourceConnector
from app.services.duplicate_checker.repository import ScholarshipDuplicateChecker
from app.services.extraction.openai_extractor import GeminiScholarshipExtractor
from app.services.filters.scholarship import ScholarshipPageFilter
from app.services.pipeline import ScholarshipDiscoveryPipeline
from app.services.validator.scholarship import ScholarshipValidator


class DiscoveryAlreadyRunning(RuntimeError):
    """Raised when a second discovery run is requested in this process."""


_discovery_lock = Lock()


def build_pipeline() -> ScholarshipDiscoveryPipeline:
    """Build the Version 1 scholarship discovery pipeline."""
    return ScholarshipDiscoveryPipeline(
        connector=UniversitySourceConnector(
            max_pages=settings.CRAWL_MAX_PAGES,
            max_depth=settings.CRAWL_MAX_DEPTH,
            timeout_ms=settings.CRAWL_TIMEOUT_MS,
        ),
        page_filter=ScholarshipPageFilter(),
        collector=RawDataCollector(settings.RAW_STORAGE_PATH),
        extractor=GeminiScholarshipExtractor(),
        validator=ScholarshipValidator(),
        duplicate_checker=ScholarshipDuplicateChecker(),
    )


async def run_scheduled_discovery() -> None:
    """Run discovery for each enabled source using isolated database sessions."""
    if not _discovery_lock.acquire(blocking=False):
        raise DiscoveryAlreadyRunning("A discovery run is already in progress")

    try:
        # Step 1: Fetch source IDs using an isolated session
        with SessionLocal() as db:
            sources = db.scalars(
                select(Source).where(Source.enabled.is_(True))
            ).all()
            source_ids = [s.id for s in sources]

        pipeline = build_pipeline()

        # Step 2: Process each source with its OWN fresh DB session
        for sid in source_ids:
            with SessionLocal() as db:
                source = db.get(Source, sid)
                if not source or not source.enabled:
                    continue
                try:
                    await pipeline.run(db, source)
                except Exception as exc:
                    print(
                        "[DISCOVERY SOURCE FAILED] "
                        f"{source.name}: {type(exc).__name__}: {exc}"
                    )
    finally:
        _discovery_lock.release()