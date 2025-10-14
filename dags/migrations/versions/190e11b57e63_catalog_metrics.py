"""catalog_metrics

Revision ID: 190e11b57e63
Revises: 6dd9cf906b06
Create Date: 2025-10-16 14:26:08.837868

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "190e11b57e63"
down_revision: Union[str, None] = "6dd9cf906b06"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "library_catalog_metrics",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("date", sa.DATE),
        sa.Column("category", sa.String(length=255), nullable=False),
        sa.Column("filter", sa.String(length=255), nullable=True),
        sa.Column("aggregation", sa.String(length=255), nullable=False),
        sa.Column("key", sa.String(length=255), nullable=False),
        sa.Column("value", sa.Float, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
    )

    op.create_unique_constraint(
        "ix_library_catalog_metrics",
        "library_catalog_metrics",
        ["category", "filter", "aggregation", "key", "date"],
    )


def downgrade():
    op.drop_table("library_catalog_metrics")

    op.drop_constraint(
        "ix_library_catalog_metrics", "library_catalog_metrics", type_="unique"
    )
