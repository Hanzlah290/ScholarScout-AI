import asyncio

from app.config.settings import settings
from app.database.session import SessionLocal
from app.models.source import Source
from app.services.connectors.university import UniversitySourceConnector
from app.services.filters.scholarship import ScholarshipPageFilter


async def main():
    db = SessionLocal()

    try:
        source = (
            db.query(Source)
            .filter(Source.base_url.like("%english.ucas.ac.cn%"))
            .filter(Source.enabled.is_(True))
            .first()
        )

        if source is None:
            raise RuntimeError("Enabled UCAS source was not found.")

        connector = UniversitySourceConnector(
            max_pages=settings.CRAWL_MAX_PAGES,
            max_depth=settings.CRAWL_MAX_DEPTH,
            timeout_ms=settings.CRAWL_TIMEOUT_MS,
        )

        pages = await connector.fetch(source)
        filtered = ScholarshipPageFilter().filter(pages)

        print(f"PAGES_SCANNED={len(pages)}")
        print(f"PAGES_FILTERED={len(filtered)}")
        print()
        print("FILTERED CANDIDATES:")
        print("=" * 100)

        for i, page in enumerate(filtered, 1):
            print(
                f"{i}. {page.url} | "
                f"{page.title} | "
                f"{page.matched_keywords}"
            )

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
