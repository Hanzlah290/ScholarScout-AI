import asyncio
from uuid import uuid4

from app.models.source import Source
from app.services.connectors.university import UniversitySourceConnector


async def main():
    source = Source(
        id=uuid4(),
        name="Beijing Institute of Technology",
        base_url="https://english.bit.edu.cn",
        status="active",
    )

    connector = UniversitySourceConnector(
        max_pages=30,
        max_depth=2,
        timeout_ms=30_000,
    )

    print("=== CONNECTOR TEST ===")
    print("Source:", source.name)
    print("Base URL:", source.base_url)

    pages = await connector.fetch(source)

    print("Pages fetched:", len(pages))

    for page in pages:
        print(
            f"{page.depth} | "
            f"{page.url} | "
            f"{page.title[:80]}"
        )


if __name__ == "__main__":
    asyncio.run(main())

