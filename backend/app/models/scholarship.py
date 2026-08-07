from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import Date, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Scholarship(Base):
    __tablename__ = "scholarships"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    source_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("sources.id"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    university: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    country: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    degree: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    field: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    funding: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    deadline: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    application_link: Mapped[str] = mapped_column(
        String(500),
        unique=True,
        nullable=False,
    )

    source_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    requirements: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    documents_required: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    ai_summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="Open",
    )

    last_verified: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    raw_page_path: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    source = relationship("Source")