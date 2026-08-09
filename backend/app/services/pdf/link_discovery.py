from __future__ import annotations

from urllib.parse import urldefrag, urljoin, urlparse

from bs4 import BeautifulSoup

from app.schemas.pipeline import DownloadedPage


class PDFLinkDiscovery:
    """Discover PDF links contained in an already downloaded HTML page."""

    def discover(
        self,
        page: DownloadedPage,
    ) -> list[str]:
        soup = BeautifulSoup(
            page.html,
            "html.parser",
        )

        pdf_urls: list[str] = []
        seen: set[str] = set()

        for anchor in soup.find_all(
            "a",
            href=True,
        ):
            href = anchor.get("href")

            if not isinstance(href, str):
                continue

            normalized = self._normalize_url(
                str(page.url),
                href,
            )

            if not normalized:
                continue

            if not self._is_pdf_url(normalized):
                continue

            if normalized in seen:
                continue

            seen.add(normalized)
            pdf_urls.append(normalized)

        return pdf_urls

    @staticmethod
    def _normalize_url(
        current_url: str,
        href: str,
    ) -> str | None:
        if not href or href.startswith(
            (
                "mailto:",
                "tel:",
                "javascript:",
                "#",
            )
        ):
            return None

        absolute = urljoin(
            current_url,
            href,
        )

        absolute, _ = urldefrag(absolute)

        parsed = urlparse(absolute)

        if parsed.scheme not in {
            "http",
            "https",
        }:
            return None

        if not parsed.netloc:
            return None

        return absolute

    @staticmethod
    def _is_pdf_url(url: str) -> bool:
        path = urlparse(url).path.lower()

        return path.endswith(".pdf")