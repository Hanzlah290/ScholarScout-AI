import asyncio
from uuid import uuid4

from app.services.pdf.downloader import PDFDownloader


PDF_URL = (
    "https://isc.bit.edu.cn/docs/"
    "/2025-10/09d8791d614341d58870f6128f9c2b1c.pdf"
)

SOURCE_PAGE_URL = (
    "https://english.bit.edu.cn/postgraduate.html"
)


async def main():
    downloader = PDFDownloader(
        storage_root="storage/test_pdfs"
    )

    result = downloader.download_and_extract(
        source_id=uuid4(),
        pdf_url=PDF_URL,
        source_page_url=SOURCE_PAGE_URL,
        title="BIT Admission Book 2026 for Master's and Ph.D Program",
    )

    print("=== PDF DOWNLOADER TEST ===")
    print("URL:", result.url)
    print("Source page:", result.source_page_url)
    print("Title:", result.title)
    print("Saved path:", result.path)
    print("Text characters:", len(result.text))
    print("Text preview:")
    print(result.text[:1000])


if __name__ == "__main__":
    asyncio.run(main())