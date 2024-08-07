"""Database revision for Annual Reports

Revision ID: fc3ffc0db6db
Revises: 101f23913167
Create Date: 2024-08-06 10:53:05.078428

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "fc3ffc0db6db"
down_revision: Union[str, None] = "101f23913167"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "annual_reports_publications",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("year", sa.Integer, nullable=False),
        sa.Column("publications", sa.Integer, nullable=False),
        sa.Column("journals", sa.Integer, nullable=False),
        sa.Column("contributions", sa.Integer, nullable=False),
        sa.Column("theses", sa.Integer, nullable=False),
        sa.Column("rest", sa.Integer, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
    )
    op.create_table(
        "annual_reports_journals",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("year", sa.Integer, nullable=False),
        sa.Column("journal", sa.String, nullable=False),
        sa.Column("count", sa.Integer, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
    )
    op.create_table(
        "annual_reports_categories",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("year", sa.Integer, nullable=False),
        sa.Column("category", sa.String, nullable=False),
        sa.Column("count", sa.Integer, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("annual_reports_publications")
    op.drop_table("annual_reports_journals")
    op.drop_table("annual_reports_categories")
