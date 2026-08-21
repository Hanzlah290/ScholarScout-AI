from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.scholarship import Scholarship
from app.schemas.pipeline import ValidatedScholarship


class ScholarshipDuplicateChecker:
    """Check for duplicate scholarship records and upsert safely."""

    def upsert(
        self,
        db: Session,
        scholarship: ValidatedScholarship,
    ) -> tuple[Scholarship, bool]:
        """
        Upsert a validated scholarship safely.
        
        Matches on application_link AND title to allow multiple distinct scholarships 
        to share a single application portal URL (e.g., http://apply.sjtu.edu.cn/).
        """
        application_link_str = str(scholarship.application_link)
        source_url_str = str(scholarship.source_url)

        # 1. Match by application_link AND title
        stmt = select(Scholarship).where(
            Scholarship.application_link == application_link_str,
            Scholarship.title == scholarship.title,
        )
        existing = db.scalars(stmt).first()

        # 2. Fallback match by source_url AND title
        if not existing:
            stmt_url = select(Scholarship).where(
                Scholarship.source_url == source_url_str,
                Scholarship.title == scholarship.title,
            )
            existing = db.scalars(stmt_url).first()

        # 3. Fallback match by title AND university
        if not existing:
            stmt_univ = select(Scholarship).where(
                Scholarship.title == scholarship.title,
                Scholarship.university == scholarship.university,
            )
            existing = db.scalars(stmt_univ).first()

        # UPDATE existing record if matched
        if existing:
            existing.source_id = scholarship.source_id
            existing.title = scholarship.title
            existing.university = scholarship.university
            existing.country = scholarship.country
            existing.degree = scholarship.degree
            existing.field = scholarship.field
            existing.funding = scholarship.funding
            existing.deadline = scholarship.deadline
            existing.application_link = application_link_str
            existing.source_url = source_url_str
            existing.requirements = scholarship.requirements
            existing.documents_required = scholarship.documents_required
            existing.ai_summary = scholarship.summary
            existing.status = scholarship.status
            existing.last_verified = datetime.now(timezone.utc)
            existing.raw_page_path = scholarship.raw_page_path
            
            return existing, False

        # CREATE new record if no match exists
        new_scholarship = Scholarship(
            source_id=scholarship.source_id,
            title=scholarship.title,
            university=scholarship.university,
            country=scholarship.country,
            degree=scholarship.degree,
            field=scholarship.field,
            funding=scholarship.funding,
            deadline=scholarship.deadline,
            application_link=application_link_str,
            source_url=source_url_str,
            requirements=scholarship.requirements,
            documents_required=scholarship.documents_required,
            ai_summary=scholarship.summary,
            status=scholarship.status,
            last_verified=datetime.now(timezone.utc),
            raw_page_path=scholarship.raw_page_path,
        )
        db.add(new_scholarship)
        return new_scholarship, True