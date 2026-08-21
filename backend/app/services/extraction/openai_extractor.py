from __future__ import annotations

from datetime import datetime
from pathlib import Path
import time

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
You are an expert data extraction agent specialized in extracting university scholarship data for ScholarScout AI Version 1.

The source material is an official Chinese university webpage or an official university PDF document.

========================
1. SCOPE & ELIGIBILITY
========================
- COUNTRY: China is the ONLY supported country.
- SOURCE: Must be an official Chinese university website or official document.
- TARGET DEGREE: Master's degree programs ONLY.
- TARGET FIELD: Software Engineering, Computer Science and Technology, Information Technology, Data Science, Artificial Intelligence, or closely related computing fields.
- EXCLUDED SCHOLARSHIPS: Chinese Government Scholarship (CSC) is strictly OUT OF SCOPE for Version 1. NEVER create a scholarship record for CSC, CGS, or China Link programs.
- NON-DEGREE EXCLUSION: Exclude language preparatory courses, exchange programs, and short-term non-degree certificates.

========================
2. SCHOLARSHIP IDENTIFICATION
========================
Set `is_scholarship` to true ONLY when the source clearly identifies an in-scope, non-CSC university or local government scholarship opportunity for Master's computing applicants.
Set `is_scholarship` to false when:
- The page is a generic news article or general non-scholarship page.
- The page only discusses CSC / Chinese Government Scholarships.
- The opportunity is strictly an internal award for currently enrolled senior students (e.g., student leadership or social contribution awards) rather than an entrance scholarship.
- There is insufficient evidence to identify a specific scholarship program.

========================
3. DEADLINE MAPPING & DUAL INTAKE RESOLUTION
========================
- PROGRAM-LEVEL INHERITANCE: If a webpage details a specific degree program (e.g., Master's in Computer Science) along with an eligible university scholarship (e.g., JSU Presidential Scholarship or University Tuition Discount), explicitly map and inherit the program's general "Application Deadline" directly to the scholarship record.
- RAW DEADLINE: Always extract and store the verbatim deadline text into `raw_deadline` (e.g., "Spring: Jan. 01, 2026 | Autumn: June 30, 2026").
- ISO DEADLINE FORMATTING (`YYYY-MM-DD`):
  1. Identify the upcoming or nearest future intake deadline relative to the provided Reference Date.
  2. If today's date is past the Spring cutoff, select the Autumn/Fall cutoff date.
  3. Format the selected intake cutoff as a strict ISO date (`YYYY-MM-DD`) in `deadline`.
  4. Never set both `deadline` and `raw_deadline` to null if any application cutoff date or intake period exists on the page.

========================
4. FACTUAL INTEGRITY & FIELD RULES
========================
- Extract only facts directly supported by the source text. Never invent, infer, or hallucinate details.
- FUNDING: Extract specific tuition discounts, monthly stipends, accommodation coverage, or insurance benefits explicitly mentioned.
- APPLICATION LINK: Use only official application URLs explicitly present in the source text. Prefer specific portal links (e.g., `https://hit.at0086.cn/student`).
- SUMMARY: Provide a concise, factual summary of the scholarship coverage and eligibility.
""".strip()


EVIDENCE_SYSTEM_PROMPT = """
You are an evidence extraction agent for ScholarScout AI Version 1.

Your task is to analyze an official Chinese university PDF document and return categorical evidence matching `PDFScholarshipEvidence`.

STRICT FIELD CATEGORIZATION:
1. `scholarship_name`: The exact official name of the scholarship.
2. `scholarship_evidence`: Verbatim quote proving the scholarship exists.
3. `funding_evidence`: Verbatim quote detailing tuition coverage, stipends, accommodation, or grants.
4. `deadline_evidence`: Verbatim quote establishing application cutoff dates or intake windows.
5. `degree_evidence`: Verbatim quote confirming Master's degree eligibility.
6. `field_evidence`: Verbatim quote confirming Software Engineering or computing field eligibility.
7. `application_evidence`: Verbatim quote containing official application portal URLs or submission instructions.

EXCLUSIONS:
- Chinese Government Scholarship (CSC) is OUT OF SCOPE. Set `is_scholarship` to false if the PDF exclusively describes CSC.
- Do not copy the same text across multiple evidence fields unless strictly necessary.
""".strip()


class GeminiScholarshipExtractor:
    """Extract scholarship data and PDF evidence using Gemini with structured JSON output."""

    def __init__(
        self,
        client: genai.Client | None = None,
        model: str | None = None,
    ) -> None:
        if client is not None:
            self.client = client
        else:
            if not settings.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY is not configured in settings")

            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

        self.model = model or settings.GEMINI_MODEL

    def _build_prompt(self, text: str, url: str, title: str) -> str:
        """Construct the prompt with dynamic execution date context."""
        current_date_str = datetime.now().strftime("%Y-%m-%d")

        return (
            f"{SYSTEM_PROMPT}\n\n"
            f"Reference Date (Today): {current_date_str}\n\n"
            "Extract the structured scholarship information from this official webpage.\n\n"
            f"Page URL: {url}\n"
            f"Page Title: {title}\n\n"
            f"Page Content:\n{text[:60_000]}"
        )

    def extract(self, page: StoredPage) -> ScholarshipExtraction:
        """Extract scholarship details with polite rate-limiting and retry backoff."""
        time.sleep(1)  # Rate limiting delay

        max_retries = 4
        backoff_delay = 3

        for attempt in range(max_retries):
            try:
                return self._call_gemini_extraction(page)
            except Exception as exc:
                err_str = str(exc).upper()
                retryable_keywords = ["429", "RESOURCE_EXHAUSTED", "503", "UNAVAILABLE", "RATE_LIMIT"]
                
                if any(k in err_str for k in retryable_keywords):
                    if attempt == max_retries - 1:
                        raise RuntimeError(f"Exceeded maximum Gemini API retries. Error: {exc}") from exc
                    
                    print(f"[RETRY {attempt + 1}/{max_retries}] Gemini transient rate limit/API error. Retrying in {backoff_delay}s...")
                    time.sleep(backoff_delay)
                    backoff_delay *= 2
                else:
                    raise

        raise RuntimeError("Failed to complete Gemini extraction due to unexpected failure.")

    def _call_gemini_extraction(self, page: StoredPage) -> ScholarshipExtraction:
        """Execute the Gemini API call and parse structured JSON against Pydantic schema."""
        html = Path(page.path).read_text(encoding="utf-8")
        text = self._clean_html(html)

        prompt = self._build_prompt(text, page.url, page.title)

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0,
                response_mime_type="application/json",
                response_json_schema=ScholarshipExtraction.model_json_schema(),
            ),
        )

        if not response.text:
            raise ValueError("Gemini returned an empty extraction response")

        return ScholarshipExtraction.model_validate_json(response.text)

    def extract_pdf(self, pdf: DownloadedPDF) -> ScholarshipExtraction:
        """Extract scholarship information from raw PDF text."""
        current_date_str = datetime.now().strftime("%Y-%m-%d")
        
        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"Reference Date (Today): {current_date_str}\n\n"
            "Extract structured scholarship information from this official PDF document.\n\n"
            f"PDF URL: {pdf.url}\n"
            f"Source Page URL: {pdf.source_page_url}\n"
            f"PDF Title: {pdf.title}\n\n"
            f"PDF Text Content:\n{pdf.text[:60_000]}"
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0,
                response_mime_type="application/json",
                response_json_schema=ScholarshipExtraction.model_json_schema(),
            ),
        )

        if not response.text:
            raise ValueError("Gemini returned an empty PDF extraction response")

        return ScholarshipExtraction.model_validate_json(response.text)

    def extract_pdf_evidence(self, pdf: DownloadedPDF) -> PDFScholarshipEvidence:
        """Extract evidence categories from an official PDF document."""
        prompt = (
            f"{EVIDENCE_SYSTEM_PROMPT}\n\n"
            "Extract structured evidence fields from this official PDF document.\n\n"
            f"PDF URL: {pdf.url}\n"
            f"Source Page URL: {pdf.source_page_url}\n"
            f"PDF Title: {pdf.title}\n\n"
            f"PDF Text Content:\n{pdf.text[:60_000]}"
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0,
                response_mime_type="application/json",
                response_json_schema=PDFScholarshipEvidence.model_json_schema(),
            ),
        )

        if not response.text:
            raise ValueError("Gemini returned an empty PDF evidence response")

        return PDFScholarshipEvidence.model_validate_json(response.text)

    @staticmethod
    def _clean_html(html: str) -> str:
        """Strip non-content HTML elements and return clean text block."""
        soup = BeautifulSoup(html, "html.parser")

        for element in soup(["script", "style", "noscript", "svg", "header", "footer"]):
            element.decompose()

        lines = (line.strip() for line in soup.get_text("\n").splitlines())
        return "\n".join(line for line in lines if line)