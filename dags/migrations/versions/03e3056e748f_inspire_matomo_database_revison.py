"""Inspire Matomo Database Revison

Revision ID: 03e3056e748f
Revises: 101f23913167
Create Date: 2024-08-08 11:07:36.748634

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "03e3056e748f"
down_revision: Union[str, None] = "101f23913167"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "inspire_matomo_data",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("visits", sa.Integer, nullable=False),
        sa.Column("unique_visitors", sa.Integer, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("inspire_matomo_data")
