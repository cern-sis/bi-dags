"""add library people counter

Revision ID: 2ff4f07d56bd
Revises: fc43c200a255
Create Date: 2025-02-07 14:00:43.307147

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2ff4f07d56bd"
down_revision: Union[str, None] = "fc43c200a255"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "library_people_counter",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("date", sa.TIMESTAMP(timezone=True), nullable=False, unique=True),
        sa.Column("occupancy", sa.Integer, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
    )


def downgrade():
    op.drop_table("library_people_counter")
