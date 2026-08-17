import asyncio

from playwright.async_api import async_playwright


URL = "https://isc.bit.edu.cn/admissionsaid/financialaid/scholarships/958501cc93dd4cf285d0e903f24432da.htm"


async def main():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=True
        )

        page = await browser.new_page()

        try:
            response = await page.goto(
                URL,
                wait_until="commit",
                timeout=60_000,
            )

            print("STATUS:", response.status if response else None)
            print("RESPONSE URL:", response.url if response else None)
            print("PAGE URL:", page.url)
            print("CONTENT TYPE:", response.headers.get("content-type") if response else None)

            if response:
                body = await response.body()

                print("RESPONSE BODY BYTES:", len(body))

                print("\n========== RESPONSE BODY ==========\n")
                print(body[:5000].decode("utf-8", errors="replace"))
                print("\n===================================\n")

            print("PAGE TITLE:", await page.title())

            html = await page.content()

            print("PAGE CONTENT LENGTH:", len(html))

            print("\n========== PAGE DOM ==========\n")
            print(html)
            print("\n==============================\n")

        finally:
            await browser.close()


asyncio.run(main())