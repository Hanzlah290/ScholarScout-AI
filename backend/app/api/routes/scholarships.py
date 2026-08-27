from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.scholarship import Scholarship
from app.models.source import Source
from app.schemas.api import ScholarshipResponse
from app.services.scheduler.service import scheduler_instance


router = APIRouter(prefix="/scholarships", tags=["scholarships"])
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.get("/stats")
def get_system_stats(db: DatabaseSession):
    """Fetch live counts, last scan timestamp, and background scheduler status."""
    open_scholarships = db.query(Scholarship).filter(Scholarship.status == "Open").count()
    sources_count = db.query(Source).count()
    
    # Get latest verified or updated scholarship timestamp for last scan
    latest_scholarship = db.query(func.max(Scholarship.updated_at)).scalar()
    last_scan_at = latest_scholarship.isoformat() if latest_scholarship else None

    # Get live scheduler status
    scheduler_info = scheduler_instance.get_status()

    return {
        "open_scholarships": open_scholarships,
        "sources_count": sources_count,
        "last_scan_at": last_scan_at,
        "is_scheduler_running": scheduler_info["running"],
        "scheduler_status": scheduler_info["status"],
        "next_run_at": scheduler_info["next_run_at"],
    }


@router.get("", response_model=list[ScholarshipResponse])
def list_scholarships(
    db: DatabaseSession,
    status_filter: str | None = Query(default=None, alias="status"),
    country: str | None = None,
    degree: str | None = None,
    field: str | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[Scholarship]:
    """List verified scholarships, with lightweight dashboard filters."""
    statement = select(Scholarship)
    if status_filter:
        statement = statement.where(Scholarship.status == status_filter)
    if country:
        statement = statement.where(Scholarship.country == country)
    if degree:
        statement = statement.where(Scholarship.degree == degree)
    if field:
        statement = statement.where(Scholarship.field == field)
    statement = statement.order_by(
        Scholarship.deadline.is_(None),
        Scholarship.deadline.asc(),
        Scholarship.created_at.desc(),
    ).limit(limit).offset(offset)
    return list(db.scalars(statement).all())


@router.get("/{scholarship_id}", response_model=ScholarshipResponse)
def get_scholarship(scholarship_id: UUID, db: DatabaseSession) -> Scholarship:
    scholarship = db.get(Scholarship, scholarship_id)
    if scholarship is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scholarship not found",
        )
    return scholarship