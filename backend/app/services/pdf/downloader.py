from __future__ import annotations

from pathlib import Path
from uuid import UUID

import requests
from pypdf import PdfReader

from app.schemas.pipeline import DownloadedPDF


class PDFDownloader:
    """Download a PDF and extract its text."""

    def __init__(
        self,
        storage_root: str = "storage/pdfs",
        timeout_seconds: int = 30,
    ) -> None:
        self.storage_root = Path(storage_root)
        self.timeout_seconds = timeout_seconds

    def download_and_extract(
        self,
        source_id: UUID,
        pdf_url: str,
        source_page_url: str,
        title: str = "",
    ) -> DownloadedPDF:
        response = requests.get(
            pdf_url,
            timeout=self.timeout_seconds,
        )

        response.raise_for_status()

        content_type = response.headers.get(
            "Content-Type",
            ""
        ).lower()

        if "application/pdf" not in content_type:
            raise ValueError(
                f"URL did not return a PDF. "
                f"Content-Type: {content_type or 'missing'}"
            )

        if not response.content:
            raise ValueError("Downloaded PDF is empty")

        filename = self._filename_from_url(pdf_url)

        source_directory = (
            self.storage_root / str(source_id)
        )
        source_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        pdf_path = source_directory / filename

        pdf_path.write_bytes(response.content)

        text = self._extract_text(pdf_path)

        return DownloadedPDF(
            source_id=source_id,
            url=pdf_url,
            title=title.strip(),
            text=text,
            path=str(pdf_path),
            source_page_url=source_page_url,
        )

    @staticmethod
    def _filename_from_url(url: str) -> str:
        filename = url.rstrip("/").split("/")[-1]

        if not filename.lower().endswith(".pdf"):
            filename = f"{filename}.pdf"

        return filename

    @staticmethod
    def _extract_text(pdf_path: Path) -> str:
        reader = PdfReader(str(pdf_path))

        pages: list[str] = []

        for page in reader.pages:
            text = page.extract_text() or ""

            if text.strip():
                pages.append(text.strip())

        return "\n\n".join(pages)