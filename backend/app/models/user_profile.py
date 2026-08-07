from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class UserProfile(Base):
    __tablename__ = "user_profile"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    target_country: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    preferred_degree: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    target_field: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    cgpa: Mapped[Decimal | None] = mapped_column(
        Numeric(4, 2),
        nullable=True,
    )

    english_test: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    preferred_language: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
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