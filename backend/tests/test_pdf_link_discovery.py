import asyncio
from uuid import uuid4

from playwright.async_api import async_playwright

from app.schemas.pipeline import DownloadedPage
from app.services.pdf.link_discovery import PDFLinkDiscovery


URL = "https://english.bit.edu.cn/postgraduate.html"


async def main():
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
        source_id=uuid4(),
        url=URL,
        title=title.strip(),
        html=html,
        depth=1,
    )

    discovery = PDFLinkDiscovery()

    pdf_urls = discovery.discover(
        downloaded_page
    )

    print("=== PDF LINK DISCOVERY TEST ===")
    print("Source page:", URL)
    print("PDF links found:", len(pdf_urls))

    for index, pdf_url in enumerate(
        pdf_urls,
        start=1,
    ):
        print(f"{index} | {pdf_url}")


if __name__ == "__main__":
    asyncio.run(main())