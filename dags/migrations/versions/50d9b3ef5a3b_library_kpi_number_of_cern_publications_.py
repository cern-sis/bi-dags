"""Library KPI: Number of CERN Publications,
contributions in conference proceedings,
Number of CERN publications
(other than journals and proceedings)

Revision ID: 50d9b3ef5a3b
Revises: 64ac526a078b
Create Date: 2024-05-08 10:27:00.634151

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "50d9b3ef5a3b"
down_revision: Union[str, None] = "64ac526a078b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "library_cern_publication_records",
        sa.Column("year", sa.Integer, primary_key=True),
        sa.Column("publications_total_count", sa.Integer, nullable=False),
        sa.Column("conference_proceedings_count", sa.Integer, nullable=False),
        sa.Column("non_journal_proceedings_count", sa.Integer, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
    )


def downgrade():
    op.drop_table("library_cern_publication_records")
