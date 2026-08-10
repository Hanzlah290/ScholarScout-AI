from datetime import date
from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.source import Source
from app.schemas.pipeline import (
    DownloadedPage,
    FilteredPage,
    ScholarshipExtraction,
    StoredPage,
    ValidatedScholarship,
)
from app.services.pipeline import ScholarshipDiscoveryPipeline


@pytest.mark.asyncio
async def test_pipeline_runs_successfully() -> None:
    source = Source(
        id=uuid4(),
        name="Example University",
        base_url="https://www.example.edu.cn",
        source_type="university",
        enabled=True,
        status="active",
    )

    page = DownloadedPage(
        source_id=source.id,
        url="https://www.example.edu.cn/scholarship",
        title="Master Scholarship",
        html="<html><body>Scholarship</body></html>",
        depth=0,
    )

    filtered_page = FilteredPage(
        **page.model_dump(),
        matched_keywords=["scholarship"],
    )

    stored_page = StoredPage(
        source_id=source.id,
        url=page.url,
        title=page.title,
        path="storage/raw_pages/example.html",
        content_hash="test-hash",
    )

    extraction = ScholarshipExtraction(
        is_scholarship=True,
        title="International Master's Scholarship",
        university="Example University",
        country="China",
        degree="Master's",
        field="Software Engineering",
        funding="Fully Funded",
        deadline=date(2099, 1, 1),
        requirements=["Bachelor's degree"],
        documents_required=["Transcript"],
        application_link="https://www.example.edu.cn/apply",
        summary="Scholarship for international Master's students.",
    )

    validated = ValidatedScholarship(
        **extraction.model_dump(),
        source_id=source.id,
        source_url=page.url,
        raw_page_path=stored_page.path,
        status="Open",
    )

    connector = MagicMock()
    connector.fetch = AsyncMock(return_value=[page])

    page_filter = MagicMock()
    page_filter.filter.return_value = [filtered_page]

    collector = MagicMock()
    collector.store.return_value = stored_page

    extractor = MagicMock()
    extractor.extract.return_value = extraction

    validator = MagicMock()
    validator.validate.return_value = validated

    duplicate_checker = MagicMock()
    duplicate_checker.upsert.return_value = (
        SimpleNamespace(title=validated.title),
        True,
    )

    db = MagicMock()

    pipeline = ScholarshipDiscoveryPipeline(
        connector=connector,
        page_filter=page_filter,
        collector=collector,
        extractor=extractor,
        validator=validator,
        duplicate_checker=duplicate_checker,
    )

    result = await pipeline.run(db, source)

    assert result.source_id == source.id
    assert result.pages_scanned == 1
    assert result.pages_filtered == 1
    assert result.scholarships_found == 1
    assert result.new_scholarships == 1
    assert result.updated_scholarships == 0

    connector.fetch.assert_awaited_once_with(source)
    page_filter.filter.assert_called_once_with([page])
    collector.store.assert_called_once_with(filtered_page)
    extractor.extract.assert_called_once_with(stored_page)
    validator.validate.assert_called_once_with(
        extraction,
        stored_page,
        source,
    )
    duplicate_checker.upsert.assert_called_once_with(
        db,
        validated,
    )

    assert source.status == "healthy"
    assert source.last_checked is not None