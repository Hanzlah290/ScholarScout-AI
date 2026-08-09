import asyncio

from playwright.async_api import async_playwright


async def main():
    url = "https://english.bit.edu.cn/postgraduate.html"

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)

        try:
            page = await browser.new_page()

            print("=== EXTERNAL PDF EVIDENCE ===")
            print("Opening:", url)
            print()

            try:
                await page.goto(
                    url,
                    wait_until="commit",
                    timeout=30_000,
                )
            except Exception as exc:
                print("Navigation warning:", exc)

            await page.wait_for_timeout(3_000)

            links = await page.locator("a[href]").evaluate_all(
                """
                els => els.map(a => ({
                    text: (a.innerText || a.textContent || "").trim(),
                    href: a.href
                }))
                """
            )

            print("Total links:", len(links))
            print()

            found = 0

            for link in links:
                text = link["text"]
                href = link["href"]

                if (
                    "isc.bit.edu.cn" in href
                    or "admission book" in text.lower()
                    or href.lower().endswith(".pdf")
                ):
                    found += 1

                    print(f"{found} | TEXT: {text}")
                    print(f"    URL:  {href}")
                    print()

            print("Matching links:", found)

        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())