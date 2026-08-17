from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.source import Source
from app.schemas.api import SourceResponse


router = APIRouter(prefix="/sources", tags=["sources"])
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[SourceResponse])
def list_sources(db: DatabaseSession) -> list[Source]:
    """List configured discovery sources and their latest health state."""
    return list(db.scalars(select(Source).order_by(Source.name)).all())