"""add people in out counter

Revision ID: 6dd9cf906b06
Revises: 2ff4f07d56bd
Create Date: 2025-02-14 09:09:05.880252

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6dd9cf906b06"
down_revision: Union[str, None] = "2ff4f07d56bd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "library_people_counter", sa.Column("people_in", sa.Integer, nullable=False)
    )
    op.add_column(
        "library_people_counter", sa.Column("people_out", sa.Integer, nullable=False)
    )


def downgrade():
    op.drop_column("library_people_counter", "people_in")
    op.drop_column("library_people_counter", "people_out")
