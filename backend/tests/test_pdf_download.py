import asyncio
from pathlib import Path

from playwright.async_api import async_playwright


PDF_URL = (
    "https://isc.bit.edu.cn/docs//2025-10/"
    "09d8791d614341d58870f6128f9c2b1c.pdf"
)

OUTPUT_DIR = Path("storage/test_pdfs")
OUTPUT_FILE = OUTPUT_DIR / "bit_admission_book_2026.pdf"


async def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=== PDF DOWNLOAD TEST ===")
    print("URL:", PDF_URL)
    print()

    async with async_playwright() as playwright:
        request = await playwright.request.new_context()

        try:
            response = await request.get(
                PDF_URL,
                timeout=30_000,
            )

            print("HTTP status:", response.status)
            print("Content-Type:", response.headers.get("content-type"))
            print("Content-Length:", response.headers.get("content-length"))
            print()

            if not response.ok:
                print("DOWNLOAD FAILED")
                return

            body = await response.body()

            OUTPUT_FILE.write_bytes(body)

            print("Downloaded bytes:", len(body))
            print("Saved to:", OUTPUT_FILE)

        finally:
            await request.dispose()

    print()
    print("File exists:", OUTPUT_FILE.exists())

    if OUTPUT_FILE.exists():
        print("File size:", OUTPUT_FILE.stat().st_size)


if __name__ == "__main__":
    asyncio.run(main())