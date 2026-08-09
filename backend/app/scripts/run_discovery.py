from __future__ import annotations

import argparse
import asyncio

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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run ScholarScout AI discovery for one university source.")
    parser.add_argument("--source-name", required=True, help="Configured university name")
    parser.add_argument("--source-url", required=True, help="Official HTTPS university base URL")
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    db = SessionLocal()
    try:
        source = db.scalar(select(Source).where(Source.base_url == args.source_url.rstrip("/")))
        if source is None:
            source = Source(
                name=args.source_name,
                base_url=args.source_url.rstrip("/"),
                source_type="university",
                enabled=True,
                status="active",
            )
            db.add(source)
            db.commit()
            db.refresh(source)

        if not source.enabled:
            raise RuntimeError(f"Source is disabled: {source.name}")

        pipeline = ScholarshipDiscoveryPipeline(
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
        result = await pipeline.run(db, source)
        print(result.model_dump_json(indent=2))
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
