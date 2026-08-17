from __future__ import annotations

import heapq
import time
from itertools import count
from urllib.parse import urldefrag, urljoin, urlparse

from playwright.async_api import Page as PlaywrightPage, async_playwright

from app.models.source import Source
from app.schemas.pipeline import DownloadedPage
from app.services.connectors.metrics import metrics_tracker


RELEVANT_URL_TERMS = (
    "scholarship",
    "scholarships",
    "funding",
    "fellowship",
    "financial",
    "admission",
    "admissions",
    "international",
    "graduate",
    "postgraduate",
    "master",
    "masters",
)


class UniversitySourceConnector:
    """Crawl one configured official university website within its own host."""

    def __init__(
        self,
        max_pages: int = 50,
        max_depth: int = 2,
        timeout_ms: int = 30_000,
    ) -> None:
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.timeout_ms = timeout_ms

    async def fetch(self, source: Source) -> list[DownloadedPage]:
        """Download HTML pages from a configured university source."""

        base_url = self._validate_base_url(source.base_url)
        base_host = urlparse(base_url).netloc.lower()

        # Priority queue:
        # lower priority number = crawled earlier
        queue: list[tuple[int, int, str, int]] = []

        counter = count()

        heapq.heappush(
            queue,
            (
                self._priority(base_url, 0),
                next(counter),
                base_url,
                0,
            ),
        )

        queued = {base_url}
        visited: set[str] = set()
        pages: list[DownloadedPage] = []

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)

            try:
                page = await browser.new_page()

                while queue and len(pages) < self.max_pages:
                    _, _, url, depth = heapq.heappop(queue)

                    if url in visited:
                        continue

                    visited.add(url)

                    # Instrumentation: measure execution duration & payload size
                    start_time = time.perf_counter()
                    failed = False
                    status_code = 0
                    html = ""
                    title = ""

                    try:
                        response = await self._load(page, url)
                        if response:
                            status_code = response.status
                        html = await page.content()
                        title = await page.title()
                    except Exception:
                        failed = True
                        status_code = 500
                    finally:
                        latency_sec = time.perf_counter() - start_time
                        response_size = len(html.encode("utf-8")) if html else 0

                        # Record network metrics into tracker
                        metrics_tracker.record_request(
                            url=url,
                            status_code=status_code,
                            response_size=response_size,
                            latency_sec=latency_sec,
                            failed=failed,
                        )

                    if failed:
                        continue

                    pages.append(
                        DownloadedPage(
                            source_id=source.id,
                            url=url,
                            title=title.strip(),
                            html=html,
                            depth=depth,
                        )
                    )

                    if depth >= self.max_depth:
                        continue

                    links = await page.locator(
                        "a[href]"
                    ).evaluate_all(
                        "els => els.map(a => a.href)"
                    )

                    for href in links:
                        normalized = self._normalize_url(
                            url,
                            href,
                        )

                        if not normalized:
                            continue

                        if self._is_non_html_resource(normalized):
                            continue

                        if normalized in queued or normalized in visited:
                            continue

                        if (
                            urlparse(normalized).netloc.lower()
                            != base_host
                        ):
                            continue

                        queued.add(normalized)

                        heapq.heappush(
                            queue,
                            (
                                self._priority(
                                    normalized,
                                    depth + 1,
                                ),
                                next(counter),
                                normalized,
                                depth + 1,
                            ),
                        )

            finally:
                await browser.close()

        return pages

    async def _load(
        self,
        page: PlaywrightPage,
        url: str,
    ):
        response = await page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=self.timeout_ms,
        )
        await page.wait_for_timeout(500)
        return response

    @staticmethod
    def _priority(url: str, depth: int) -> int:
        path = urlparse(url).path.lower()
        score = 0

        for term in RELEVANT_URL_TERMS:
            if term in path:
                if term in {
                    "scholarship",
                    "scholarships",
                    "funding",
                    "fellowship",
                    "financial",
                }:
                    score += 5
                else:
                    score += 2

        return (depth * 3) - score

    @staticmethod
    def _validate_base_url(url: str) -> str:
        parsed = urlparse(url)

        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError(
                "University source base_url must be a valid HTTPS URL"
            )

        return url.rstrip("/")

    @staticmethod
    def _is_non_html_resource(url: str) -> bool:
        path = urlparse(url).path.lower()

        return path.endswith(
            (
                ".pdf",
                ".doc",
                ".docx",
                ".xls",
                ".xlsx",
                ".ppt",
                ".pptx",
                ".jpg",
                ".jpeg",
                ".png",
                ".gif",
                ".svg",
                ".zip",
            )
        )

    @staticmethod
    def _normalize_url(
        current_url: str,
        href: str,
    ) -> str | None:
        if not href:
            return None
            
        href = href.strip()
        if href.startswith(
            (
                "mailto:",
                "tel:",
                "javascript:",
                "#",
                "void(0)",
            )
        ):
            return None

        absolute = urljoin(current_url, href)
        absolute, _ = urldefrag(absolute)

        parsed = urlparse(absolute)

        if parsed.scheme not in {"http", "https"}:
            return None

        if not parsed.netloc:
            return None

        # Filter out static assets or fragment-only links
        path_lower = parsed.path.lower()
        if path_lower.endswith(
            (
                ".css", ".js", ".png", ".jpg", ".jpeg", ".gif", 
                ".svg", ".ico", ".woff", ".woff2", ".ttf", ".eot"
            )
        ):
            return None

        return absolute.rstrip("/")