from __future__ import annotations

from pathlib import Path

from bs4 import BeautifulSoup
from google import genai
from google.genai import types

from app.config.settings import settings
from app.schemas.pipeline import (
    DownloadedPDF,
    PDFScholarshipEvidence,
    ScholarshipExtraction,
    StoredPage,
)


SYSTEM_PROMPT = """
You extract scholarship data for ScholarScout AI Version 1.

The source material is an official Chinese university webpage or an official
university PDF.

IMPORTANT SCOPE:

- Version 1 supports scholarships offered by official Chinese university
  sources.
- China is the only supported country.
- The target degree is Master's.
- The target field is Software Engineering or a closely related computing
  field.
- Chinese Government Scholarship (CSC) is OUT OF SCOPE for Version 1.
- Never create a CSC scholarship record.

EVIDENCE RULES:

- Extract only facts directly supported by the supplied source text.
- Never invent, infer, or guess missing information.
- Do not treat the existence of a scholarship application form as proof that
  the entire document describes a specific scholarship.
- Do not treat a general admission guide as a specific scholarship opportunity
  unless the source contains clear evidence identifying the scholarship.
- Do not infer a scholarship deadline from a general university admission
  deadline.
- Do not infer funding amounts, accommodation benefits, insurance, stipends,
  or tuition coverage unless those details are explicitly supported.
- If the source does not provide sufficient evidence for a specific
  scholarship opportunity, set is_scholarship to false.
- When is_scholarship is false, do not invent scholarship-specific details.

SCHOLARSHIP IDENTIFICATION:

Set is_scholarship to true only when the source itself clearly identifies a
specific scholarship opportunity relevant to the target.

- Identify the exact scholarship name from the source.
- The scholarship name must be supported directly by the source.

Set is_scholarship to false when:

- the source is only a general admission guide;
- scholarship evidence is too vague;
- only a scholarship application form is mentioned;
- the source discusses CSC / Chinese Government Scholarship;
- the scholarship does not match the target degree or field;
- there is insufficient evidence to identify a specific in-scope scholarship.

TARGET:

- Target degree: Master's.
- Target field: Software Engineering or a closely related computing field.
- Computer Science and Technology may qualify as closely related.
- Do not assume every Master's program qualifies.

DEADLINES:

- Use YYYY-MM-DD only when the source explicitly supports that specific
  scholarship deadline.
- Do not convert a general admission deadline into a scholarship deadline.
- If the scholarship deadline cannot be established, use null.

APPLICATION LINK:

- Use only an official application URL explicitly supported by the source.
- Prefer the most specific official application URL.
- Never invent or modify an application URL.

REQUIREMENTS AND DOCUMENTS:

- Include only concise factual items explicitly supported by the source.
- Do not add requirements that are merely typical for scholarships.

FUNDING:

- Include only funding details explicitly supported by the source.
- Never infer "full scholarship" from a general scholarship reference.

SUMMARY:

- Keep the summary concise and factual.
- Do not claim that a scholarship exists when the evidence is insufficient.
""".strip()


EVIDENCE_SYSTEM_PROMPT = """
You extract scholarship EVIDENCE from an official Chinese university PDF
for ScholarScout AI Version 1.

Your job is NOT to summarize the PDF.

Your job is to identify and separately return direct evidence for exactly these
fields:

1. scholarship_name
2. scholarship_evidence
3. funding_evidence
4. deadline_evidence
5. degree_evidence
6. field_evidence
7. application_evidence

STRICT SEPARATION RULES:

SCHOLARSHIP NAME:
- scholarship_name must contain ONLY the exact scholarship name.
- Do not put funding, deadline, degree, field, or application information
  inside scholarship_name.

SCHOLARSHIP EVIDENCE:
- scholarship_evidence must contain only text supporting that the named
  scholarship exists.
- Do not use this field for funding, deadline, degree, field, or application
  details unless that text is necessary to identify the scholarship.

FUNDING EVIDENCE:
- funding_evidence must contain ONLY evidence describing scholarship funding,
  such as tuition coverage, stipend, accommodation, insurance, grants,
  scholarships amounts, or award amounts.
- Do NOT include study duration, degree duration, program duration,
  degree eligibility, field information, or application deadlines.
- If the source gives both funding and study duration in the same sentence,
  extract only the funding portion when possible.
- Do not put deadlines or application URLs here.

DEADLINE EVIDENCE:
- deadline_evidence must contain ONLY evidence about the scholarship's
  application/award deadline or application period.
- Do not use a general university admission deadline unless the source
  explicitly connects it to the identified scholarship.
- If no scholarship-specific deadline is supported, leave this field empty.

DEGREE EVIDENCE:
- degree_evidence must contain ONLY evidence identifying the eligible degree.
- The target is Master's.
- Study duration may be included when it directly describes the target
  Master's degree.
- Do not put funding amounts, scholarship benefits, deadlines, fields,
  or application URLs here.

FIELD EVIDENCE:
- field_evidence must contain ONLY evidence identifying the eligible field
  or program.
- Software Engineering and closely related computing fields are relevant.
- Computer Science and Technology may qualify.
- Do not put degree, funding, or deadline information here.

APPLICATION EVIDENCE:
- application_evidence must contain ONLY the official application URL or
  direct evidence identifying the official application route.
- Do not put funding, deadline, degree, or field information here.

IMPORTANT:

- Extract only facts directly supported by the PDF.
- Never invent or infer missing information.
- Chinese Government Scholarship (CSC) is OUT OF SCOPE for Version 1.
- If the PDF describes CSC / Chinese Government Scholarship, set
  is_scholarship to false and explain this in excluded_reason.
- A general admission guide is not automatically a scholarship.
- A scholarship application form alone is not sufficient evidence.
- If a field is not supported, leave it empty.
- Do not copy the same evidence into multiple fields unless absolutely
  necessary.
- Keep each evidence field focused on its own category.

Return JSON matching PDFScholarshipEvidence.
""".strip()


class GeminiScholarshipExtractor:
    """Extract scholarship data and PDF evidence using Gemini."""

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
        page: StoredPage,
    ) -> ScholarshipExtraction:
        html = Path(page.path).read_text(
            encoding="utf-8"
        )

        text = self._clean_html(html)

        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            "Extract the scholarship information from this official "
            "university page.\n\n"
            f"Page URL: {page.url}\n"
            f"Page title: {page.title}\n\n"
            f"Page text:\n{text[:60_000]}"
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0,
                response_mime_type="application/json",
                response_json_schema=(
                    ScholarshipExtraction.model_json_schema()
                ),
            ),
        )

        if not response.text:
            raise ValueError(
                "Gemini returned an empty extraction response"
            )

        return ScholarshipExtraction.model_validate_json(
            response.text
        )

    def extract_pdf(
        self,
        pdf: DownloadedPDF,
    ) -> ScholarshipExtraction:
        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            "Extract the scholarship information from this official "
            "university PDF.\n\n"
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
                    ScholarshipExtraction.model_json_schema()
                ),
            ),
        )

        if not response.text:
            raise ValueError(
                "Gemini returned an empty PDF extraction response"
            )

        return ScholarshipExtraction.model_validate_json(
            response.text
        )

    def extract_pdf_evidence(
        self,
        pdf: DownloadedPDF,
    ) -> PDFScholarshipEvidence:
        prompt = (
            f"{EVIDENCE_SYSTEM_PROMPT}\n\n"
            "Extract scholarship evidence from this official "
            "university PDF.\n\n"
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

    @staticmethod
    def _clean_html(
        html: str,
    ) -> str:
        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        for element in soup(
            ["script", "style", "noscript", "svg"]
        ):
            element.decompose()

        return "\n".join(
            line.strip()
            for line in soup.get_text("\n").splitlines()
            if line.strip()
        )