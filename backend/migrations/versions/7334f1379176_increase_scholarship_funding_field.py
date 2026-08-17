"""increase scholarship funding field

Revision ID: 7334f1379176
Revises: c7fc87bf2713
Create Date: 2026-08-12 21:50:38.097141
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7334f1379176"
down_revision: Union[str, Sequence[str], None] = "c7fc87bf2713"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "scholarships",
        "funding",
        existing_type=sa.VARCHAR(length=100),
        type_=sa.Text(),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "scholarships",
        "funding",
        existing_type=sa.Text(),
        type_=sa.VARCHAR(length=100),
        existing_nullable=False,
    )