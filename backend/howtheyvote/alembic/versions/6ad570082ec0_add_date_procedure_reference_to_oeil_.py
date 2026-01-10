"""Add date, procedure_reference to OEIL summaries

Revision ID: 6ad570082ec0
Revises: 0d47f2a76c65
Create Date: 2026-01-09 13:13:03.007281

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "6ad570082ec0"
down_revision = "0d47f2a76c65"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("oeil_summaries", sa.Column("date", sa.DateTime))
    op.add_column("oeil_summaries", sa.Column("procedure_reference", sa.Unicode))


def downgrade() -> None:
    op.drop_column("oeil_summaries", "date")
    op.drop_column("oeil_summaries", "procedure_reference")
