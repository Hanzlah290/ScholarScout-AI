import pytest
from datetime import date

from app.database.session import SessionLocal
from app.models.source import Source
from app.schemas.pipeline import DownloadedPage
from app.services.collector.filesystem import RawDataCollector
from app.services.filters.scholarship import ScholarshipPageFilter
from app.services.extraction.openai_extractor import GeminiScholarshipExtractor
from app.services.validator.scholarship import ScholarshipValidator
from app.services.duplicate_checker.repository import ScholarshipDuplicateChecker


BIT_URL = (
    "https://isc.bit.edu.cn/admissionsaid/financialaid/scholarships/b112925.htm"
)
pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_real_bit_scholarship_page(tmp_path) -> None:
    from playwright.async_api import async_playwright

    db = SessionLocal()

    try:
        source = (
            db.query(Source)
            .filter(Source.base_url == "https://isc.bit.edu.cn")
            .first()
        )

        if source is None:
            source = Source(
                name="Beijing Institute of Technology - ISC",
                base_url="https://isc.bit.edu.cn",
                source_type="university",
                enabled=True,
                status="active",
            )
            db.add(source)
            db.commit()
            db.refresh(source)

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(
                headless=True
            )

            page = await browser.new_page()

            response = await page.goto(
            BIT_URL,
            wait_until="commit",
            timeout=60_000,
            )

            assert response is not None
            assert response.status == 200

            html = await response.body()

            assert html, "BIT returned an empty response body."

            html_text = html.decode("utf-8", errors="replace")

            assert len(html_text) > 10_000, (
            f"BIT scholarship page returned unexpectedly small HTML: "
            f"{len(html_text)} bytes"
            )

            assert "Study in BIT Scholarship" in html_text

            await page.wait_for_timeout(500)

            html = await page.content()
            title = await page.title()

            await browser.close()

        downloaded = DownloadedPage(
            source_id=source.id,
            url=BIT_URL,
            title=title,
            html=html,
            depth=0,
        )

        print("\nREAL WEBSITE TEST")
        print("URL:", downloaded.url)
        print("TITLE:", downloaded.title)
        print("HTML SIZE:", len(downloaded.html))

        # --------------------------------------------------
        # 1. FILTER
        # --------------------------------------------------

        page_filter = ScholarshipPageFilter()

        filtered = page_filter.filter(
            [downloaded]
        )

        assert filtered, (
            "The real BIT scholarship page was rejected "
            "by the scholarship filter."
        )

        print(
            "FILTER PASSED:",
            filtered[0].matched_keywords,
        )

        # --------------------------------------------------
        # 2. RAW COLLECTION
        # --------------------------------------------------

        collector = RawDataCollector(tmp_path)

        stored = collector.store(
            filtered[0]
        )

        print(
            "RAW PAGE STORED:",
            stored.path,
        )

        # --------------------------------------------------
        # 3. GEMINI EXTRACTION
        # --------------------------------------------------

        extractor = GeminiScholarshipExtractor()

        extraction = extractor.extract(
            stored
        )

        print("\nGEMINI RESULT:")
        print(
            extraction.model_dump_json(
                indent=2
            )
        )

        # --------------------------------------------------
        # 4. VALIDATION
        # --------------------------------------------------

        validator = ScholarshipValidator()

        validated = validator.validate(
            extraction,
            stored,
            source,
        )

        print("\nVALIDATION PASSED")
        print("Title:", validated.title)
        print("University:", validated.university)
        print("Country:", validated.country)
        print("Degree:", validated.degree)
        print("Field:", validated.field)
        print("Deadline:", validated.deadline)
        print("Status:", validated.status)
        assert validated.status in {"Open", "Closed"}

        # --------------------------------------------------
        # 5. DATABASE
        # --------------------------------------------------

        duplicate_checker = (
            ScholarshipDuplicateChecker()
        )

        scholarship, is_new = (
            duplicate_checker.upsert(
                db,
                validated,
            )
        )

        db.commit()

        print("\nDATABASE PASSED")
        print("Scholarship ID:", scholarship.id)
        print("New record:", is_new)

        assert scholarship.id is not None
        assert scholarship.country == "China"
        assert "master" in scholarship.degree.lower()

    finally:
        db.close()