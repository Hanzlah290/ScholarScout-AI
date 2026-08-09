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
  or tuition coverage unless those details are explicitly supported by the
  supplied source.
- If the source does not provide sufficient evidence for a specific
  scholarship opportunity, set is_scholarship to false.
- When is_scholarship is false, do not invent scholarship-specific details.

SCHOLARSHIP IDENTIFICATION:

Set is_scholarship to true only when the source itself clearly identifies a
specific scholarship opportunity relevant to the target.

- Before setting is_scholarship=true, identify the exact scholarship name
  from the source text.
- The scholarship name must be supported by the source itself.

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
- A computing field such as Computer Science and Technology may qualify as
  closely related.
- Do not assume that every Master's program in a university qualifies.

DEADLINES:

- Use an ISO date (YYYY-MM-DD) only when the source explicitly supports that
  specific scholarship deadline.
- Do not convert a general admission/application period into a scholarship
  deadline.
- If a scholarship deadline cannot be established, use null.

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

OUTPUT:
Return structured data matching the provided scholarship schema.
""".strip()


EVIDENCE_SYSTEM_PROMPT = """
You extract scholarship evidence from official Chinese university webpages
or official university PDFs for ScholarScout AI Version 1.

Your job is NOT to create a scholarship summary.

Your job is to identify a specific scholarship opportunity and place each
piece of evidence into the CORRECT evidence field.

VERSION 1 SCOPE:

- Country: China only.
- Source must be an official Chinese university source.
- Target degree: Master's.
- Target field: Software Engineering or a closely related computing field.
- Chinese Government Scholarship (CSC) is OUT OF SCOPE.
- Never accept or create a CSC scholarship record.

STRICT EVIDENCE SEPARATION:

1. scholarship_name
- Contains ONLY the exact name of the scholarship.
- Copy the scholarship name from the source when possible.
- Do NOT put funding information here.
- Do NOT put degree, field, deadline, or application information here.
- Example:
  "Beijing Government Scholarship"

2. scholarship_evidence
- Contains ONLY source text proving that the named scholarship exists.
- It should identify the scholarship or clearly describe the scholarship
  opportunity.
- Do NOT put funding amounts here unless they are necessary to identify the
  scholarship.
- Do NOT put degree or field information here unless needed to identify the
  scholarship.

3. funding_evidence
- Contains ONLY evidence about financial benefits.
- This may include tuition coverage, tuition waivers, accommodation,
  accommodation subsidies, insurance, stipends, grants, or award amounts.
- Include the amount and unit when explicitly provided.
- Do NOT put degree information here.
- Do NOT put deadline information here.
- Do NOT put application URLs here.

4. deadline_evidence
- Contains ONLY evidence about the application deadline or scholarship
  deadline.
- Include the date and the surrounding wording that explicitly connects the
  date to the scholarship.
- Do NOT use a general university admission deadline unless the source
  explicitly identifies it as the deadline for this scholarship.
- If the source does not clearly connect a date to the scholarship, return
  an empty string.
- Do NOT put funding, degree, or field information here.

5. degree_evidence
- Contains ONLY evidence identifying the eligible degree level.
- For this Version 1 target, this should normally contain evidence that the
  scholarship applies to Master's students/programs.
- Examples:
  "Master's students"
  "Applicants for master's degree programs"
- Do NOT put funding amounts here.
- Do NOT put field names here.
- Do NOT put deadlines here.

6. field_evidence
- Contains ONLY evidence identifying the eligible academic field/program.
- The field must be Software Engineering or a closely related computing field.
- Examples:
  "Computer Science and Technology"
  "Software Engineering"
- Do NOT put funding information here.
- Do NOT put degree information here unless the source text is inseparable
  and specifically identifies the program.
- Do NOT put deadlines here.

7. application_evidence
- Contains ONLY evidence of the official application URL or application
  method for the scholarship.
- Prefer the exact official application URL stated in the source.
- Do NOT put scholarship names, funding, deadlines, degree, or field
  information here.
- Never invent or modify a URL.

8. excluded_reason
- Leave empty when the scholarship is accepted.
- When is_scholarship is false, briefly explain why the source should not be
  accepted.
- Examples:
  "Chinese Government Scholarship (CSC) is outside Version 1 scope."
  "No specific scholarship opportunity could be identified."
  "Scholarship does not apply to the target Master's computing field."

SCHOLARSHIP ACCEPTANCE:

Set is_scholarship=true ONLY when ALL of the following are sufficiently
supported by the source:

- A specific scholarship can be identified.
- The scholarship is not CSC.
- The scholarship is relevant to Master's study.
- The scholarship applies to Software Engineering or a closely related
  computing field.
- The source provides enough evidence to identify the opportunity.

If these conditions are not sufficiently supported:

- Set is_scholarship=false.
- Leave unsupported evidence fields empty.
- Explain the rejection in excluded_reason.
- Never guess missing information.

IMPORTANT:

Each evidence field has ONE purpose.

Never move information from one category into another category just because
the information is available.

For example:

WRONG:
degree_evidence = "Master student: CNY 20,000/person"

CORRECT:
funding_evidence = "Master student: CNY 20,000/person"

And:

WRONG:
field_evidence = "Master's students: CNY 20,000/person"

CORRECT:
degree_evidence = "Master's students"

And:

WRONG:
deadline_evidence = "Master's students: CNY 20,000/person"

CORRECT:
deadline_evidence = only the scholarship deadline evidence.

If a category has no reliable evidence, return an empty string.

OUTPUT:

Return ONLY structured data matching the PDFScholarshipEvidence schema.
Do not create additional fields.
"""



class GeminiScholarshipExtractor:
    """Extract scholarship data from HTML pages and PDFs using Gemini."""

    def __init__(
        self,
        client: genai.Client | None = None,
        model: str | None = None,
    ) -> None:
        if client is not None:
            self.client = client
        else:
            if not settings.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY is not configured")

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
        "Analyze the following official university PDF.\n\n"
        f"PDF URL: {pdf.url}\n"
        f"Source page URL: {pdf.source_page_url}\n"
        f"PDF title: {pdf.title}\n\n"
        "SOURCE TEXT:\n"
        f"{pdf.text[:60_000]}"
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
    def _clean_html(html: str) -> str:
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
