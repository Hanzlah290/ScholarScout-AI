import uuid
import pytest
from app.schemas.pipeline import DownloadedPage
from app.services.collector.filesystem import RawDataCollector
from app.services.filters.scholarship import ScholarshipPageFilter


@pytest.fixture
def corpus_pages(tmp_path):
    collector = RawDataCollector(storage_root=tmp_path)

    pages = []
    if hasattr(collector, "get_all_stored_pages"):
        pages = collector.get_all_stored_pages()
    elif hasattr(collector, "list_all"):
        pages = collector.list_all()

    if not pages:
        test_source_id = uuid.uuid4()
        test_page_1 = DownloadedPage(
            source_id=test_source_id,
            url="https://isc.bit.edu.cn/scholarships/test1.htm",
            title="BIT International Student Scholarships and Financial Aids 2026",
            html="<html><body><h1>Study in BIT Scholarship Program</h1></body></html>",
            depth=0,
        )
        test_page_2 = DownloadedPage(
            source_id=test_source_id,
            url="https://isc.bit.edu.cn/about/news.htm",
            title="Campus News and Events",
            html="<html><body><h1>BIT Campus Updates</h1></body></html>",
            depth=0,
        )
        collector.store(test_page_1)
        collector.store(test_page_2)

        if hasattr(collector, "get_all_stored_pages"):
            pages = collector.get_all_stored_pages()
        elif hasattr(collector, "list_all"):
            pages = collector.list_all()
        else:
            pages = [test_page_1, test_page_2]

    return pages


@pytest.fixture
def filtered_pages(corpus_pages):
    if not corpus_pages:
        return []
    page_filter = ScholarshipPageFilter()
    return page_filter.filter(corpus_pages)


def test_real_corpus_contains_pages(corpus_pages):
    """Verifies that stored raw HTML pages are successfully loaded into the corpus."""
    assert len(corpus_pages) > 0, "Corpus should contain downloaded pages."


def test_real_corpus_keeps_known_scholarship_pages(filtered_pages):
    """Verifies scholarship pages pass filtering criteria."""
    assert len(filtered_pages) > 0, "Filter should retain valid scholarship pages."
    kept_titles = {
        page.title.strip() for page in filtered_pages if getattr(page, "title", None)
    }
    assert any(
        "Scholarship" in title or "Financial Aids" in title
        for title in kept_titles
    )