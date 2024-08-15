"""Change year column type from Integer to Date in annual reports tables

Revision ID: db8ba01db969
Revises: fc3ffc0db6db
Create Date: 2024-08-15 16:09:05.042861

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision: str = "db8ba01db969"
down_revision: Union[str, None] = "fc3ffc0db6db"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "annual_reports_publications", sa.Column("year_temp", sa.Date(), nullable=True)
    )
    op.add_column(
        "annual_reports_journals", sa.Column("year_temp", sa.Date(), nullable=True)
    )
    op.add_column(
        "annual_reports_categories", sa.Column("year_temp", sa.Date(), nullable=True)
    )

    publications = table(
        "annual_reports_publications",
        column("year", sa.Integer),
        column("year_temp", sa.Date),
    )
    journals = table(
        "annual_reports_journals",
        column("year", sa.Integer),
        column("year_temp", sa.Date),
    )
    categories = table(
        "annual_reports_categories",
        column("year", sa.Integer),
        column("year_temp", sa.Date),
    )

    conn = op.get_bind()
    conn.execute(
        publications.update().values(
            year_temp=sa.func.date(
                sa.func.concat(op.inline_literal(""), publications.c.year, "-01-01")
            )
        )
    )
    conn.execute(
        journals.update().values(
            year_temp=sa.func.date(
                sa.func.concat(op.inline_literal(""), journals.c.year, "-01-01")
            )
        )
    )
    conn.execute(
        categories.update().values(
            year_temp=sa.func.date(
                sa.func.concat(op.inline_literal(""), categories.c.year, "-01-01")
            )
        )
    )

    op.drop_column("annual_reports_publications", "year")
    op.drop_column("annual_reports_journals", "year")
    op.drop_column("annual_reports_categories", "year")

    op.alter_column(
        "annual_reports_publications",
        "year_temp",
        new_column_name="year",
        existing_type=sa.Date(),
        nullable=False,
    )
    op.alter_column(
        "annual_reports_journals",
        "year_temp",
        new_column_name="year",
        existing_type=sa.Date(),
        nullable=False,
    )
    op.alter_column(
        "annual_reports_categories",
        "year_temp",
        new_column_name="year",
        existing_type=sa.Date(),
        nullable=False,
    )


def downgrade():
    op.add_column(
        "annual_reports_publications", sa.Column("year", sa.Integer, nullable=False)
    )
    op.add_column(
        "annual_reports_journals", sa.Column("year", sa.Integer, nullable=False)
    )
    op.add_column(
        "annual_reports_categories", sa.Column("year", sa.Integer, nullable=False)
    )

    publications = table("annual_reports_publications", column("year", sa.Date))
    journals = table("annual_reports_journals", column("year", sa.Date))
    categories = table("annual_reports_categories", column("year", sa.Date))

    conn = op.get_bind()
    conn.execute(
        publications.update().values(year=sa.func.extract("year", publications.c.year))
    )
    conn.execute(
        journals.update().values(year=sa.func.extract("year", journals.c.year))
    )
    conn.execute(
        categories.update().values(year=sa.func.extract("year", categories.c.year))
    )

    op.drop_column("annual_reports_publications", "year_temp")
    op.drop_column("annual_reports_journals", "year_temp")
    op.drop_column("annual_reports_categories", "year_temp")
