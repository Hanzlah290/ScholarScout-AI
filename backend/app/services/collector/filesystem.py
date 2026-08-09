from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

from app.schemas.pipeline import FilteredPage, StoredPage


class RawDataCollector:
    """Persist filtered HTML pages outside PostgreSQL for later reprocessing."""

    def __init__(self, storage_root: Path | str = "storage/raw_pages") -> None:
        self.storage_root = Path(storage_root)

    def store(self, page: FilteredPage) -> StoredPage:
        content_hash = hashlib.sha256(page.html.encode("utf-8")).hexdigest()
        now = datetime.now(timezone.utc)
        directory = self.storage_root / str(page.source_id) / now.strftime("%Y/%m/%d")
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{content_hash}.html"
        path.write_text(page.html, encoding="utf-8")

        return StoredPage(
            source_id=page.source_id,
            url=page.url,
            title=page.title,
            path=str(path),
            content_hash=content_hash,
        )
