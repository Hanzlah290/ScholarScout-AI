from __future__ import annotations

from app.schemas.pipeline import DownloadedPDF, DownloadedPage
from app.services.pdf.downloader import PDFDownloader
from app.services.pdf.link_discovery import PDFLinkDiscovery


class PDFProcessor:
    """Discover and download PDFs linked from an HTML page."""

    def __init__(
        self,
        link_discovery: PDFLinkDiscovery,
        downloader: PDFDownloader,
    ) -> None:
        self.link_discovery = link_discovery
        self.downloader = downloader

    def process(
        self,
        page: DownloadedPage,
    ) -> list[DownloadedPDF]:
        pdf_urls = self.link_discovery.discover(page)

        results: list[DownloadedPDF] = []

        for pdf_url in pdf_urls:
            try:
                downloaded = self.downloader.download_and_extract(
                    source_id=page.source_id,
                    pdf_url=pdf_url,
                    source_page_url=str(page.url),
                    title="",
                )
            except Exception as exc:
                print(
                    f"[PDF DOWNLOAD FAILED] "
                    f"{pdf_url}: "
                    f"{type(exc).__name__}: {exc}"
                )
                continue

            results.append(downloaded)

        return results