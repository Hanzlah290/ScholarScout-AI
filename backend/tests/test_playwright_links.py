import asyncio

from playwright.async_api import async_playwright


async def main():
    url = "https://english.bit.edu.cn/postgraduate.html"

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)

        try:
            page = await browser.new_page()

            await page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=30_000,
            )

            await page.wait_for_timeout(500)

            links = await page.locator(
                "a[href]"
            ).evaluate_all(
                "els => els.map(a => a.href)"
            )

            print("=== PLAYWRIGHT LINKS ===")
            print("Total links:", len(links))

            for link in links:
                if (
                    "scholar" in link.lower()
                    or "admission" in link.lower()
                    or "master" in link.lower()
                    or "postgraduate" in link.lower()
                    or "international" in link.lower()
                    or link.lower().endswith((".htm", ".html"))
                ):
                    print(link)

        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())