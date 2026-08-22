from __future__ import annotations

from datetime import datetime, timezone
from time import monotonic

from sqlalchemy.orm import Session

from app.models.search_log import SearchLog
from app.models.source import Source
from app.schemas.pipeline import PipelineResult
from app.services.collector.filesystem import RawDataCollector
from app.services.connectors.university import UniversitySourceConnector
from app.services.duplicate_checker.repository import ScholarshipDuplicateChecker
from app.services.extraction.openai_extractor import GeminiScholarshipExtractor
from app.services.filters.scholarship import ScholarshipPageFilter
from app.services.validator.scholarship import ScholarshipValidator


class ScholarshipDiscoveryPipeline:
    """Run the Version 1 scholarship discovery workflow for one source."""

    def __init__(
        self,
        connector: UniversitySourceConnector,
        page_filter: ScholarshipPageFilter,
        collector: RawDataCollector,
        extractor: GeminiScholarshipExtractor,
        validator: ScholarshipValidator,
        duplicate_checker: ScholarshipDuplicateChecker,
    ) -> None:
        self.connector = connector
        self.page_filter = page_filter
        self.collector = collector
        self.extractor = extractor
        self.validator = validator
        self.duplicate_checker = duplicate_checker

    async def run(
        self,
        db: Session,
        source: Source,
    ) -> PipelineResult:
        started_at = datetime.now(timezone.utc)
        started = monotonic()

        log = SearchLog(
            source_id=source.id,
            started_at=started_at,
            status="running",
        )
        db.add(log)
        db.commit()

        try:
            pages = await self.connector.fetch(source)
            filtered = self.page_filter.filter(pages)

            new_count = 0
            updated_count = 0

            for page in filtered:
                stored = self.collector.store(page)

                try:
                    extraction = self.extractor.extract(stored)

                    validated = self.validator.validate(
                        extraction,
                        stored,
                        source,
                    )

                    _, is_new = self.duplicate_checker.upsert(
                        db,
                        validated,
                    )

                    if is_new:
                        new_count += 1
                    else:
                        updated_count += 1

                except ValueError as exc:
                    print(
                        f"[VALIDATION SKIPPED] "
                        f"{stored.url}: {exc}"
                    )
                    continue

                except Exception as exc:
                    print(
                        f"[EXTRACTION FAILED] "
                        f"{stored.url}: "
                        f"{type(exc).__name__}: {exc}"
                    )
                    continue

            db.commit()

            return PipelineResult(
                source_id=source.id,
                pages_scanned=len(pages),
                pages_filtered=len(filtered),
                scholarships_found=(
                    new_count + updated_count
                ),
                new_scholarships=new_count,
                updated_scholarships=updated_count,
            )

        except Exception as exc:
            db.rollback()

            finished_at = datetime.now(timezone.utc)

            log = db.get(SearchLog, log.id)

            if log:
                log.finished_at = finished_at
                log.duration_seconds = int(
                    monotonic() - started
                )
                log.status = "failed"
                log.error_message = str(exc)
                db.commit()

            raise
