from __future__ import annotations

from typing import Optional
from urllib.parse import urlparse, urlunparse

from sqlalchemy.orm import Session
from app.models.source import Source


class SourceValidator:
    """Validates, canonicalizes, and qualifies potential Chinese university sources."""

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
        "csc.edu.cn",
    }

    @classmethod
    def normalize_url(cls, raw_url: str) -> Optional[str]:
        """Canonicalize a raw URL into a clean root base_url."""
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

            netloc = netloc.split(":")[0]

            if netloc.startswith("www."):
                netloc = netloc[4:]

            return urlunparse(("https", netloc, "", "", "", ""))
        except Exception:
            return None

    @classmethod
    def is_qualifying_domain(cls, canonical_url: str) -> bool:
        """Verify if the canonical URL belongs to an eligible Chinese higher education domain."""
        if not canonical_url:
            return False

        try:
            parsed = urlparse(canonical_url)
            domain = parsed.netloc.lower()

            if any(disqualified in domain for disqualified in cls.DISQUALIFIED_DOMAINS):
                return False

            if domain.endswith(".edu.cn"):
                return True

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

        existing = db.query(Source).filter(Source.base_url == canonical_url).first()
        if existing:
            return True

        alt_variant = canonical_url.replace("https://", "https://www.")
        existing_variant = db.query(Source).filter(Source.base_url == alt_variant).first()
        return existing_variant is not None

    @classmethod
    def validate_candidate(cls, db: Session, raw_url: str) -> tuple[bool, Optional[str], str]:
        """Full validation lifecycle: Normalize -> Qualify -> Check Duplicates."""
        canonical_url = cls.normalize_url(raw_url)
        if not canonical_url:
            return False, None, "Invalid or unparseable URL format"

        if not cls.is_qualifying_domain(canonical_url):
            return False, canonical_url, "Domain does not meet Chinese university eligibility criteria"

        if cls.is_duplicate(db, canonical_url):
            return False, canonical_url, "Source domain already exists in database"

        return True, canonical_url, "Qualified and eligible"