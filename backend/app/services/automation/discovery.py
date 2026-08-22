from __future__ import annotations

import logging
import re
import urllib.parse
from typing import List
import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.models.source import Source
from app.services.automation.source_validator import SourceValidator

logger = logging.getLogger(__name__)


class SourceDiscoveryEngine:
    """Discovers prospective Chinese university portals via targeted search engine queries."""

    TARGET_SEARCH_QUERIES = [
        "site:.edu.cn scholarship master computer science",
        "site:.edu.cn scholarship software engineering master",
        "site:.edu.cn international students scholarship master",
        "site:.edu.cn master scholarship artificial intelligence",
        "site:.edu.cn graduate scholarship computer science and technology",
    ]

    def __init__(self, timeout_sec: float = 15.0) -> None:
        self.timeout_sec = timeout_sec
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }

    async def discover_candidate_urls(self) -> List[str]:
        """Executes targeted web search queries to collect candidate university links."""
        candidate_urls: List[str] = []

        async with httpx.AsyncClient(timeout=self.timeout_sec, follow_redirects=True, headers=self.headers) as client:
            for query in self.TARGET_SEARCH_QUERIES:
                try:
                    encoded_query = urllib.parse.quote_plus(query)
                    search_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"

                    response = await client.get(search_url)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, "html.parser")
                        for a_tag in soup.find_all("a", class_="result__url"):
                            href = a_tag.get("href")
                            if href:
                                clean_url = self._extract_clean_url(href)
                                if clean_url:
                                    candidate_urls.append(clean_url)
                except Exception as exc:
                    logger.warning(f"[SOURCE DISCOVERY] Search failed for query '{query}': {exc}")

        return list(set(candidate_urls))

    @staticmethod
    def _extract_clean_url(raw_href: str) -> str:
        """Strips search engine redirect wrappers to obtain the direct target URL."""
        if "uddg=" in raw_href:
            parsed = urllib.parse.urlparse(raw_href)
            query_params = urllib.parse.parse_qs(parsed.query)
            if "uddg" in query_params:
                return query_params["uddg"][0]
        return raw_href

    @staticmethod
    def derive_source_name(canonical_url: str) -> str:
        """Derives a human-readable source title from the canonical domain name."""
        try:
            domain = urllib.parse.urlparse(canonical_url).netloc
            clean_name = re.sub(r"\.(edu\.cn|cn)$", "", domain, flags=re.IGNORECASE)
            parts = [part.capitalize() for part in clean_name.split(".") if part not in ["www", "oec", "study", "admissions", "yjs", "iscen", "sie"]]
            if parts:
                return f"{' '.join(parts).upper()} University"
            return f"{domain.upper()} Portal"
        except Exception:
            return "Official Chinese University Portal"

    async def run_discovery(self, db: Session) -> List[Source]:
        """
        Executes full discovery: Fetch Candidate URLs -> Normalize & Qualify -> Save to PostgreSQL.
        Newly discovered sources are assigned next_check_at = NOW() for immediate processing.
        """
        logger.info("[SOURCE DISCOVERY] Starting targeted university source discovery...")
        candidate_urls = await self.discover_candidate_urls()
        logger.info(f"[SOURCE DISCOVERY] Collected {len(candidate_urls)} candidate URLs from web search.")

        newly_created_sources: List[Source] = []

        for raw_url in candidate_urls:
            is_valid, canonical_url, reason = SourceValidator.validate_candidate(db, raw_url)
            if is_valid and canonical_url:
                source_name = self.derive_source_name(canonical_url)
                
                new_source = Source(
                    name=source_name,
                    base_url=canonical_url,
                    source_type="university",
                    enabled=True,
                    status="active",
                    consecutive_failures=0
                )
                db.add(new_source)
                try:
                    db.commit()
                    db.refresh(new_source)
                    newly_created_sources.append(new_source)
                    logger.info(f"[SOURCE DISCOVERY] Added new source: {source_name} ({canonical_url})")
                except Exception as e:
                    db.rollback()
                    logger.error(f"[SOURCE DISCOVERY] Failed to persist source {canonical_url}: {e}")

        logger.info(f"[SOURCE DISCOVERY] Completed. Added {len(newly_created_sources)} new qualified sources.")
        return newly_created_sources