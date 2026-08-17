from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.scholarship import Scholarship
from app.schemas.api import ScholarshipResponse


router = APIRouter(prefix="/scholarships", tags=["scholarships"])
DatabaseSession = Annotated[Session, Depends(get_db)]


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