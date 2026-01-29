"""Add name to stat

Revision ID: 76aed23dc731
Revises: 190e11b57e63
Create Date: 2026-01-27 09:03:30.489696

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "76aed23dc731"
down_revision: Union[str, None] = "190e11b57e63"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "library_catalog_metrics",
        sa.Column("note", sa.String(length=255), nullable=True),
    )


def downgrade():
    op.drop_column("library_catalog_metrics", "note")
