from pathlib import Path
from uuid import UUID

from app.services.filters.scholarship import ScholarshipPageFilter
from app.schemas.pipeline import DownloadedPage


ROOT = Path(
    "storage/raw_pages/"
    "6beb2337-c77f-44d0-9d63-cc65859cf866/"
    "2026/08/08"
)

SOURCE_ID = UUID(
    "6beb2337-c77f-44d0-9d63-cc65859cf866"
)

filter_ = ScholarshipPageFilter()

pages = []

for path in ROOT.glob("*.html"):
    html = path.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    page = DownloadedPage(
        source_id=SOURCE_ID,
        url=f"https://english.bit.edu.cn/{path.name}",
        title=path.name,
        html=html,
    )

    pages.append(page)


filtered = filter_.filter(pages)

print()
print("=== ACTUAL FILTER RESULT ===")
print("Pages scanned:", len(pages))
print("Pages passing filter:", len(filtered))
print()

for page in filtered:
    print(page.url)
    print("  matched:", page.matched_keywords)
    print()