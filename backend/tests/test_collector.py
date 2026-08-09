from pathlib import Path
from uuid import uuid4

from app.schemas.pipeline import FilteredPage
from app.services.collector.filesystem import RawDataCollector


def test_collector_stores_html(tmp_path) -> None:
    page = FilteredPage(
        source_id=uuid4(),
        url="https://example.edu.cn/scholarship",
        title="Scholarship",
        html="<html><body>Scholarship details</body></html>",
        matched_keywords=["scholarship"],
    )

    stored = RawDataCollector(tmp_path).store(page)

    assert stored.path.endswith(".html")
    assert stored.content_hash
    assert stored.url == page.url
    assert Path(stored.path).exists()
