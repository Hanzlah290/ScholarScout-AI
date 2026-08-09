from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.scholarship import Scholarship
from app.schemas.pipeline import ValidatedScholarship


class ScholarshipDuplicateChecker:
    """Insert new scholarships or update an existing matching record."""

    def upsert(self, db: Session, scholarship: ValidatedScholarship) -> tuple[Scholarship, bool]:
        application_link = str(scholarship.application_link)
        source_url = str(scholarship.source_url)

        existing = db.scalar(
            select(Scholarship).where(
                Scholarship.application_link == application_link
            )
        )

        if existing is None:
            existing = db.scalar(
                select(Scholarship).where(
                    Scholarship.title == scholarship.title,
                    Scholarship.university == scholarship.university,
                )
            )

        if existing is None:
            existing = db.scalar(
                select(Scholarship).where(
                    Scholarship.source_url == source_url,
                    Scholarship.title == scholarship.title,
                )
            )

        if existing is None:
            existing = Scholarship(
                source_id=scholarship.source_id,
                title=scholarship.title,
                university=scholarship.university,
                country=scholarship.country,
                degree=scholarship.degree,
                field=scholarship.field,
                funding=scholarship.funding,
                deadline=scholarship.deadline,
                application_link=str(scholarship.application_link),
                source_url=str(scholarship.source_url),
                requirements=scholarship.requirements,
                documents_required=scholarship.documents_required,
                ai_summary=scholarship.summary,
                status=scholarship.status,
                last_verified=datetime.now(timezone.utc),
                raw_page_path=scholarship.raw_page_path,
            )
            db.add(existing)
            return existing, True

        existing.source_id = scholarship.source_id
        existing.title = scholarship.title
        existing.university = scholarship.university
        existing.country = scholarship.country
        existing.degree = scholarship.degree
        existing.field = scholarship.field
        existing.funding = scholarship.funding
        existing.deadline = scholarship.deadline
        existing.application_link = str(scholarship.application_link)
        existing.source_url = str(scholarship.source_url)
        existing.requirements = scholarship.requirements
        existing.documents_required = scholarship.documents_required
        existing.ai_summary = scholarship.summary
        existing.status = scholarship.status
        existing.last_verified = datetime.now(timezone.utc)
        existing.raw_page_path = scholarship.raw_page_path
        return existing, False
