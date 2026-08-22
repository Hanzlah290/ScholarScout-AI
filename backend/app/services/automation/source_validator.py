from __future__ import annotations

import re
from typing import Optional
from urllib.parse import urlparse, urlunparse

from sqlalchemy.orm import Session
from app.models.source import Source


class SourceValidator:
    """Validates, canonicalizes, and qualifies potential Chinese university sources."""

    # Explicit list of excluded non-university domains and aggregators
    DISQUALIFIED_DOMAINS = {
        "facebook.com",
        "twitter.com",
        "x.com",
        "linkedin.com",
        "youtube.com",
        "instagram.com",
        "wikipedia.org",
        "scholarships.com",
        "scholarshipdb.net",
        "cucas.cn",
        "chinesescholarshipcouncil.com",
        "csc.edu.cn",  # CSC is explicitly out of scope for v1
    }

    @classmethod
    def normalize_url(cls, raw_url: str) -> Optional[str]:
        """
        Canonicalize a raw URL into a clean root base_url.
        Example: 'http://www.jsu.edu.cn/admissions/master?id=1' -> 'https://jsu.edu.cn'
        """
        if not raw_url or not isinstance(raw_url, str):
            return None

        url = raw_url.strip()
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        try:
            parsed = urlparse(url)
            netloc = parsed.netloc.lower()

            if not netloc:
                return None

            # Remove port if present
            netloc = netloc.split(":")[0]

            # Strip leading 'www.' for root domain consistency
            if netloc.startswith("www."):
                netloc = netloc[4:]

            # Always enforce HTTPS for standard base URLs
            return urlunparse(("https", netloc, "", "", "", ""))
        except Exception:
            return None

    @classmethod
    def is_qualifying_domain(cls, canonical_url: str) -> bool:
        """
        Verify if the canonical URL belongs to an eligible Chinese higher education domain.
        Must end with .edu.cn (or be a recognized Chinese university domain) and not be an aggregator.
        """
        if not canonical_url:
            return False

        try:
            parsed = urlparse(canonical_url)
            domain = parsed.netloc.lower()

            # Reject known non-university/aggregator domains
            if any(disqualified in domain for disqualified in cls.DISQUALIFIED_DOMAINS):
                return False

            # Primary Rule: Chinese educational domain restriction (.edu.cn)
            if domain.endswith(".edu.cn"):
                return True

            # Secondary Rule: Allow Chinese domain extensions (.cn) if it contains university keywords
            if domain.endswith(".cn") and any(k in domain for k in ["univ", "edu", "pj"]):
                return True

            return False
        except Exception:
            return False

    @classmethod
    def is_duplicate(cls, db: Session, canonical_url: str) -> bool:
        """Check if the canonical base_url already exists in PostgreSQL sources table."""
        if not canonical_url:
            return True

        # Check exact canonical URL match
        existing = db.query(Source).filter(Source.base_url == canonical_url).first()
        if existing:
            return True

        # Check alternate protocol or www variants
        alt_variant = canonical_url.replace("https://", "https://www.")
        existing_variant = db.query(Source).filter(Source.base_url == alt_variant).first()
        return existing_variant is not None

    @classmethod
    def validate_candidate(cls, db: Session, raw_url: str) -> tuple[bool, Optional[str], str]:
        """
        Full validation lifecycle: Normalize -> Qualify -> Check Duplicates.
        Returns: (is_valid, canonical_url, reason)
        """
        canonical_url = cls.normalize_url(raw_url)
        if not canonical_url:
            return False, None, "Invalid or unparseable URL format"

        if not cls.is_qualifying_domain(canonical_url):
            return False, canonical_url, "Domain does not meet Chinese university eligibility criteria"

        if cls.is_duplicate(db, canonical_url):
            return False, canonical_url, "Source domain already exists in database"

        return True, canonical_url, "Qualified and eligible"