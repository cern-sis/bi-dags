"""Library KPIs: New items in the institutional repository

Revision ID: 101f23913167
Revises: 50d9b3ef5a3b
Create Date: 2024-07-05 17:55:10.676310

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "101f23913167"
down_revision: Union[str, None] = "50d9b3ef5a3b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "library_items_in_the_institutional_repository",
        sa.Column("year", sa.Integer, primary_key=True),
        sa.Column("inspire_arxiv_records", sa.Integer, nullable=False),
        sa.Column("inspire_curators_records", sa.Integer, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
    )


def downgrade():
    op.drop_table("library_items_in_the_institutional_repository")
