from __future__ import annotations

from pathlib import Path

from bs4 import BeautifulSoup
from google import genai
from google.genai import types

from app.config.settings import settings
from app.schemas.pipeline import ScholarshipExtraction, StoredPage


SYSTEM_PROMPT = """
You extract scholarship data from official Chinese university webpages for
ScholarScout AI Version 1.

Return structured data matching the provided scholarship schema.

Rules:

- Extract only facts supported by the webpage.
- Never invent missing information.
- country must be China.
- is_scholarship must be false when the page is not actually about a scholarship
  opportunity.
- The target degree is Master's.
- The target field is Software Engineering or a closely related computing field.
- Use an ISO date (YYYY-MM-DD) for deadline when an explicit deadline can be
  determined; otherwise use null.
- application_link must be the official application URL stated on the page.
- Prefer the most specific official application URL.
- requirements and documents_required must contain concise factual items.
- summary must be concise and factual.
- If a field cannot be supported by the webpage, leave it empty/null according
  to the schema rather than guessing.
""".strip()


class GeminiScholarshipExtractor:
    """Extract a scholarship object from a stored raw page using Gemini."""

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
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

        self.model = model or settings.GEMINI_MODEL

    def extract(self, page: StoredPage) -> ScholarshipExtraction:
        html = Path(page.path).read_text(encoding="utf-8")
        text = self._clean_html(html)

        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            "Extract the scholarship information from this official university page.\n\n"
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
                response_json_schema=ScholarshipExtraction.model_json_schema(),
            ),
        )

        if not response.text:
            raise ValueError("Gemini returned an empty extraction response")

        return ScholarshipExtraction.model_validate_json(response.text)

    @staticmethod
    def _clean_html(html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")

        for element in soup(["script", "style", "noscript", "svg"]):
            element.decompose()

        return "\n".join(
            line.strip()
            for line in soup.get_text("\n").splitlines()
            if line.strip()
        )