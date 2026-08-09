import asyncio

from playwright.async_api import async_playwright


URLS = [
    "https://english.bit.edu.cn/officeofadmissions.html",
    "https://english.bit.edu.cn/postgraduate.html",
]


async def main():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)

        try:
            page = await browser.new_page()

            for url in URLS:
                print()
                print("=" * 80)
                print("PAGE:", url)
                print("=" * 80)

                await page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=30_000,
                )

                await page.wait_for_timeout(500)

                links = await page.locator(
                    "a[href]"
                ).evaluate_all(
                    "els => els.map(a => ({href: a.href, text: a.innerText.trim()}))"
                )

                print("Links found:", len(links))

                for link in links:
                    print(
                        f"{link['text'][:60]:60} | "
                        f"{link['href']}"
                    )

        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())