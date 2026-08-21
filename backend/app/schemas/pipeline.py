from __future__ import annotations

from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, field_validator


class DownloadedPage(BaseModel):
    source_id: UUID
    url: HttpUrl
    title: str = ""
    html: str
    depth: int = Field(default=0, ge=0)

class DownloadedPDF(BaseModel):
    source_id: UUID
    url: HttpUrl
    title: str = ""
    text: str
    path: str
    source_page_url: HttpUrl


class PDFScholarshipEvidence(BaseModel):
    is_scholarship: bool = False

    scholarship_name: str = ""

    scholarship_evidence: str = ""
    funding_evidence: str = ""
    deadline_evidence: str = ""
    degree_evidence: str = ""
    field_evidence: str = ""
    application_evidence: str = ""

    excluded_reason: str = ""




class FilteredPage(DownloadedPage):
    matched_keywords: list[str] = Field(default_factory=list)


class StoredPage(BaseModel):
    source_id: UUID
    url: HttpUrl
    title: str = ""
    path: str
    content_hash: str


class ScholarshipExtraction(BaseModel):
    is_scholarship: bool = True
    title: str
    university: str
    country: str
    degree: str
    field: str
    funding: str
    deadline: date | None = None          # Parsed ISO date (YYYY-MM-DD)
    raw_deadline: str | None = None      # Textual deadline ("In October", "June 1 for Sept intake")
    requirements: list[str] = Field(default_factory=list)
    documents_required: list[str] = Field(default_factory=list)
    application_link: HttpUrl
    summary: str

    @field_validator("title", "university", "country", "degree", "field", "funding", "summary")
    @classmethod
    def non_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("field must not be empty")
        return value


class ValidatedScholarship(ScholarshipExtraction):
    source_id: UUID
    source_url: HttpUrl
    raw_page_path: str
    status: str


class PipelineResult(BaseModel):
    source_id: UUID
    pages_scanned: int = 0
    pages_filtered: int = 0
    scholarships_found: int = 0
    new_scholarships: int = 0
    updated_scholarships: int = 0
