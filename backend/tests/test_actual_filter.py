from pathlib import Path
from uuid import UUID

from bs4 import BeautifulSoup
import pytest

from app.schemas.pipeline import DownloadedPage
from app.services.filters.scholarship import ScholarshipPageFilter


ROOT = Path("storage/raw_pages")
FILTER = ScholarshipPageFilter()
pytestmark = pytest.mark.integration


def _load_pages() -> list[DownloadedPage]:
    pages = []

    for path in ROOT.rglob("*.html"):
        html = path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        soup = BeautifulSoup(html, "html.parser")

        title = (
            soup.title.get_text(" ", strip=True)
            if soup.title
            else path.stem
        )

        # storage/raw_pages/<source_id>/YYYY/MM/DD/file.html
        source_id = UUID(path.parents[3].name)

        pages.append(
            DownloadedPage(
                source_id=source_id,
                url=f"https://example.edu.cn/{path.stem}",
                title=title,
                html=html,
            )
        )

    return pages


@pytest.fixture(scope="module")
def corpus_pages():
    return _load_pages()


@pytest.fixture(scope="module")
def filtered_pages(corpus_pages):
    return FILTER.filter(corpus_pages)


def test_real_corpus_contains_pages(corpus_pages):
    """Runtime storage grows as discoveries are collected; its count is not fixed."""
    assert corpus_pages


def test_real_corpus_rejects_known_academic_template_noise(filtered_pages):
    filtered = filtered_pages

    noise_titles = {
        "Majors",
        "Colleges & Institutes",
        "Graduate",
        "Overview",
        "Schools and Offices",
        "Leadership and Governance",
        "Our Story",
        "Facts and Figures",
        "Careers",
        "Beijing Institute of Technology",
    }

    assert not any(
        page.title.strip() in noise_titles
        for page in filtered
    )


def test_real_corpus_keeps_known_scholarship_pages(filtered_pages):
    filtered = filtered_pages

    kept_titles = {
        page.title.strip()
        for page in filtered
    }

    assert any("Financial Aids" in title for title in kept_titles)
    assert any(
        "Chinese Government Scholarship" in title
        for title in kept_titles
    )
    assert any(
        "CAS-ANSO Scholarship" in title
        for title in kept_titles
    )