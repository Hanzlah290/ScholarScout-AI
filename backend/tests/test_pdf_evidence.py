from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from app.schemas.pipeline import DownloadedPDF
from app.services.extraction.pdf_evidence import (
    PDFScholarshipEvidenceExtractor,
)


PDF_PATH = Path(
    "storage/test_pdfs/processor/"
    "34bbb163-555f-4eda-aa7c-4860883a8ea5/"
    "09d8791d614341d58870f6128f9c2b1c.pdf"
)

PDF_URL = (
    "https://isc.bit.edu.cn/docs//2025-10/"
    "09d8791d614341d58870f6128f9c2b1c.pdf"
)

SOURCE_PAGE_URL = (
    "https://english.bit.edu.cn/postgraduate.html"
)


def main() -> None:
    print("=== PDF EVIDENCE EXTRACTION TEST ===")

    if not PDF_PATH.exists():
        raise FileNotFoundError(
            f"Test PDF not found: {PDF_PATH}"
        )

    reader = PdfReader(str(PDF_PATH))

    pages: list[str] = []

    for page in reader.pages:
        text = page.extract_text() or ""

        if text.strip():
            pages.append(text.strip())

    text = "\n\n".join(pages)

    print(f"PDF: {PDF_PATH}")
    print(f"Pages: {len(reader.pages)}")
    print(f"Extracted characters: {len(text)}")
    print("Sending PDF text to Gemini...")

    pdf = DownloadedPDF(
        source_id=(
            "34bbb163-555f-4eda-aa7c-4860883a8ea5"
        ),
        url=PDF_URL,
        title="BIT Admission Book 2026",
        text=text,
        path=str(PDF_PATH),
        source_page_url=SOURCE_PAGE_URL,
    )

    extractor = PDFScholarshipEvidenceExtractor()

    evidence = extractor.extract(pdf)

    print()
    print("=== EVIDENCE RESULT ===")
    print(evidence.model_dump_json(indent=2))


if __name__ == "__main__":
    main()