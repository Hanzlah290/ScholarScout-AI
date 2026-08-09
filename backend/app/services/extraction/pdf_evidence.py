from __future__ import annotations

from google import genai
from google.genai import types

from app.config.settings import settings
from app.schemas.pipeline import (
    DownloadedPDF,
    PDFScholarshipEvidence,
)


SYSTEM_PROMPT = """
You identify scholarship evidence from official Chinese university PDFs
for ScholarScout AI Version 1.

Your job is ONLY to identify and quote evidence from the supplied PDF text.

Do NOT create a final scholarship record.

Rules:

- Use only information explicitly supported by the PDF text.
- Never invent information.
- Identify specific scholarship names only when the PDF explicitly provides
  enough evidence to identify them.
- If the PDF is not actually about a scholarship opportunity, set
  is_scholarship to false.
- The target degree is Master's.
- The target field is Software Engineering or a closely related computing
  field.
- Record the exact or near-exact supporting evidence for each field.
- Do not infer a scholarship deadline from a general admission deadline.
- If no scholarship-specific deadline is supported, leave deadline_evidence
  empty.
- If multiple scholarships are mentioned, identify the evidence for the
  scholarship that is most clearly supported by the surrounding text.
- If CSC / Chinese Government Scholarship is mentioned, do not silently
  replace it with another scholarship.
- application_evidence must contain only an official application URL that
  is explicitly supported by the PDF.
- If evidence is missing, leave that field empty.
- excluded_reason should explain why the document should not proceed only
  when there is clear evidence that it should be excluded.

Return JSON matching the PDFScholarshipEvidence schema.
""".strip()


class PDFScholarshipEvidenceExtractor:
    """Extract scholarship evidence from a downloaded PDF."""

    def __init__(
        self,
        client: genai.Client | None = None,
        model: str | None = None,
    ) -> None:
        if client is not None:
            self.client = client
        else:
            if not settings.GEMINI_API_KEY:
                raise ValueError(
                    "GEMINI_API_KEY is not configured"
                )

            self.client = genai.Client(
                api_key=settings.GEMINI_API_KEY
            )

        self.model = model or settings.GEMINI_MODEL

    def extract(
        self,
        pdf: DownloadedPDF,
    ) -> PDFScholarshipEvidence:
        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            "Analyze this official university PDF.\n\n"
            f"PDF URL: {pdf.url}\n"
            f"Source page URL: {pdf.source_page_url}\n"
            f"PDF title: {pdf.title}\n\n"
            f"PDF text:\n{pdf.text[:60_000]}"
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0,
                response_mime_type="application/json",
                response_json_schema=(
                    PDFScholarshipEvidence.model_json_schema()
                ),
            ),
        )

        if not response.text:
            raise ValueError(
                "Gemini returned an empty PDF evidence response"
            )

        return PDFScholarshipEvidence.model_validate_json(
            response.text
        )
