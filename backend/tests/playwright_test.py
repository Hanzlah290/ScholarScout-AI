import asyncio
from playwright.async_api import async_playwright

async def main():
    print("Starting Playwright...")

    async with async_playwright() as p:
        print("Playwright started")

        browser = await p.chromium.launch(headless=True)
        print("Chromium launched")

        page = await browser.new_page()
        await page.goto("https://example.com")

        print("Page title:", await page.title())

        await browser.close()
        print("Browser closed")


if __name__ == "__main__":
    asyncio.run(main())
