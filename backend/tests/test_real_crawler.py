import asyncio
from uuid import uuid4

from app.models.source import Source
from app.services.connectors.university import UniversitySourceConnector
from app.services.connectors.metrics import metrics_tracker


async def main():
    source = Source(
        id=uuid4(),
        name="Beijing Institute of Technology",
        base_url="https://english.bit.edu.cn",
        status="active",
    )

    connector = UniversitySourceConnector(
        max_pages=15,
        max_depth=2,
        timeout_ms=30_000,
    )

    print("Starting ScholarScout crawler test...")
    print("Source:", source.name)
    print("Base URL:", source.base_url)

    pages = await connector.fetch(source)

    print(f"\nPages downloaded: {len(pages)}")
    for page in pages[:5]:  # Print first 5
        print(f"[{page.depth}] {page.url} | {page.title[:60]}")

    print("\n=== CRAWLER METRICS BASELINE ===")
    print(metrics_tracker.get_report())


if __name__ == "__main__":
    asyncio.run(main())