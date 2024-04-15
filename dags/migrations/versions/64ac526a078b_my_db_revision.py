"""My DB Revision

Revision ID: 64ac526a078b
Revises: 4438ef06e0c7
Create Date: 2024-04-11 16:06:50.691527

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "64ac526a078b"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("CREATE SCHEMA IF NOT EXISTS oa")
    op.create_table(
        "oa.open_access",
        sa.Column("year", sa.Integer, primary_key=True),
        sa.Column("closed_access", sa.Integer, nullable=False),
        sa.Column("bronze_open_access", sa.Integer, nullable=False),
        sa.Column("green_open_access", sa.Integer, nullable=False),
        sa.Column("gold_open_access", sa.Integer, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
        schema="oa",
    )

    op.create_table(
        "oa.golden_open_access",
        sa.Column("year", sa.Integer, primary_key=True),
        sa.Column("cern_read_and_publish", sa.Integer, nullable=False),
        sa.Column("cern_individual_apcs", sa.Integer, nullable=False),
        sa.Column("scoap3", sa.Integer, nullable=False),
        sa.Column("other", sa.Integer, nullable=False),
        sa.Column("other_colectives", sa.Integer, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
        schema="oa",
    )


def downgrade():
    op.drop_table("oa.golden_open_access", schema="oa")
    op.drop_table("oa.open_access", schema="oa")
