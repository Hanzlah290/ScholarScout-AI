from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ScholarshipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source_id: UUID
    title: str
    university: str
    country: str
    degree: str
    field: str
    funding: str
    deadline: date | None
    application_link: str
    source_url: str
    requirements: list[str] | None
    documents_required: list[str] | None
    ai_summary: str | None
    status: str
    last_verified: datetime | None
    created_at: datetime
    updated_at: datetime


class SourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    base_url: str
    source_type: str
    enabled: bool
    last_checked: datetime | None
    status: str
    created_at: datetime
    updated_at: datetime