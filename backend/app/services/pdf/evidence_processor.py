from __future__ import annotations

from app.schemas.pipeline import (
    DownloadedPDF,
    PDFScholarshipEvidence,
)
from app.services.extraction.openai_extractor import (
    GeminiScholarshipExtractor,
)
from app.services.pdf.evidence_validator import (
    PDFEvidenceValidator,
)


class PDFEvidenceProcessor:
    """
    Process one downloaded PDF through:

        PDF
        ↓
        Gemini evidence extraction
        ↓
        deterministic evidence validation

    This service does not modify the existing HTML pipeline.
    """

    def __init__(
        self,
        extractor: GeminiScholarshipExtractor,
        validator: PDFEvidenceValidator,
    ) -> None:
        self.extractor = extractor
        self.validator = validator

    def process(
        self,
        pdf: DownloadedPDF,
    ) -> PDFScholarshipEvidence | None:
        """
        Return validated PDF evidence when the PDF is in scope.

        Return None when:
        - extraction fails
        - evidence is invalid
        - scholarship is outside Version 1 scope
        """

        try:
            evidence = self.extractor.extract_pdf_evidence(pdf)

        except Exception as exc:
            print(
                "[PDF EVIDENCE EXTRACTION FAILED] "
                f"{pdf.url}: "
                f"{type(exc).__name__}: {exc}"
            )
            return None

        accepted, reason = self.validator.validate(
            evidence
        )

        if not accepted:
            print(
                "[PDF EVIDENCE REJECTED] "
                f"{pdf.url}: {reason}"
            )
            return None

        print(
            "[PDF EVIDENCE ACCEPTED] "
            f"{pdf.url}: "
            f"{evidence.scholarship_name}"
        )

        return evidence