from pypdf import PdfReader

from app.schemas.pipeline import DownloadedPDF
from app.services.extraction.openai_extractor import (
    GeminiScholarshipExtractor,
)
from app.services.pdf.evidence_processor import (
    PDFEvidenceProcessor,
)
from app.services.pdf.evidence_validator import (
    PDFEvidenceValidator,
)


def main() -> None:
    print("=== PDF EVIDENCE PROCESSOR TEST ===")

    pdf_path = (
        "storage/test_pdfs/processor/"
        "34bbb163-555f-4eda-aa7c-4860883a8ea5/"
        "09d8791d614341d58870f6128f9c2b1c.pdf"
    )

    reader = PdfReader(pdf_path)

    pdf_text = "\n\n".join(
        page.extract_text() or ""
        for page in reader.pages
    )

    print(f"PDF pages: {len(reader.pages)}")
    print(f"Extracted characters: {len(pdf_text)}")

    pdf = DownloadedPDF(
        source_id="00000000-0000-0000-0000-000000000001",
        url=(
            "https://isc.bit.edu.cn/docs//2025-10/"
            "09d8791d614341d58870f6128f9c2b1c.pdf"
        ),
        title="BIT Admission Book 2026",
        text=pdf_text,
        path=pdf_path,
        source_page_url=(
            "https://english.bit.edu.cn/"
            "postgraduate.html"
        ),
    )

    print("Creating Gemini extractor...")
    extractor = GeminiScholarshipExtractor()

    print("Creating PDF evidence validator...")
    validator = PDFEvidenceValidator()

    print("Creating PDF evidence processor...")
    processor = PDFEvidenceProcessor(
        extractor=extractor,
        validator=validator,
    )

    print("Processing PDF through evidence pipeline...")
    evidence = processor.process(pdf)

    print()
    print("=== PROCESSOR RESULT ===")

    if evidence is None:
        print("PDF was rejected or evidence extraction failed.")
        return

    print("PDF accepted.")
    print("Scholarship name:", evidence.scholarship_name)
    print("Scholarship evidence:", evidence.scholarship_evidence)
    print("Funding evidence:", evidence.funding_evidence)
    print("Deadline evidence:", evidence.deadline_evidence)
    print("Degree evidence:", evidence.degree_evidence)
    print("Field evidence:", evidence.field_evidence)
    print("Application evidence:", evidence.application_evidence)
    print("Excluded reason:", evidence.excluded_reason)


if __name__ == "__main__":
    main()