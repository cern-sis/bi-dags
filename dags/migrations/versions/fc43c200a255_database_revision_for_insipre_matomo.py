"""Database revision for Insipre Matomo

Revision ID: fc43c200a255
Revises: db8ba01db969
Create Date: 2024-08-15 17:20:55.998545

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "fc43c200a255"
down_revision: Union[str, None] = "db8ba01db969"
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
