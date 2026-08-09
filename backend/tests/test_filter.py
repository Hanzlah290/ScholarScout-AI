from pathlib import Path
from bs4 import BeautifulSoup

from app.services.filters.scholarship import ScholarshipPageFilter


root = Path(
    "storage/raw_pages/"
    "6beb2337-c77f-44d0-9d63-cc65859cf866/"
    "2026/08/08"
)

filter_ = ScholarshipPageFilter()

files = list(root.glob("*.html"))

print("\n--- LOCAL FILTER TEST ---")
print("Files found:", len(files))
print()

for path in files:
    html = path.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    soup = BeautifulSoup(html, "html.parser")

    for element in soup(
        ["script", "style", "noscript", "svg"]
    ):
        element.decompose()

    text = soup.get_text(
        " ",
        strip=True,
    ).lower()

    strong = [
        keyword
        for keyword in filter_.strong_keywords
        if keyword in text
    ]

    supporting = [
        keyword
        for keyword in filter_.supporting_keywords
        if keyword in text
    ]

    print(path.name)
    print("  Strong:", strong)
    print("  Supporting:", supporting)
    print()