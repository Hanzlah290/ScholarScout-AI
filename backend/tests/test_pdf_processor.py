import asyncio
from uuid import uuid4

from playwright.async_api import async_playwright

from app.schemas.pipeline import DownloadedPage
from app.services.pdf.downloader import PDFDownloader
from app.services.pdf.link_discovery import PDFLinkDiscovery
from app.services.pdf.processor import PDFProcessor


URL = "https://english.bit.edu.cn/postgraduate.html"


async def main():
    source_id = uuid4()

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=True
        )

        try:
            page = await browser.new_page()

            await page.goto(
                URL,
                wait_until="domcontentloaded",
                timeout=60_000,
            )

            await page.wait_for_timeout(500)

            html = await page.content()
            title = await page.title()

        finally:
            await browser.close()

    downloaded_page = DownloadedPage(
        source_id=source_id,
        url=URL,
        title=title.strip(),
        html=html,
        depth=1,
    )

    processor = PDFProcessor(
        link_discovery=PDFLinkDiscovery(),
        downloader=PDFDownloader(
            storage_root="storage/test_pdfs/processor",
            timeout_seconds=30,
        ),
    )

    pdfs = processor.process(downloaded_page)

    print("=== PDF PROCESSOR TEST ===")
    print("Source page:", URL)
    print("PDFs processed:", len(pdfs))

    for index, pdf in enumerate(
        pdfs,
        start=1,
    ):
        print()
        print(f"PDF {index}")
        print("URL:", pdf.url)
        print("Source page:", pdf.source_page_url)
        print("Saved path:", pdf.path)
        print("Text characters:", len(pdf.text))
        print("Text preview:")
        print(pdf.text[:300])


if __name__ == "__main__":
    asyncio.run(main())