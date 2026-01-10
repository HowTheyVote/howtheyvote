"""Add position_counts column to oeil_summaries table

Revision ID: 0d47f2a76c65
Revises: bb4067c7fee7
Create Date: 2026-01-09 11:54:47.206973

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0d47f2a76c65"
down_revision = "bb4067c7fee7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("oeil_summaries", sa.Column("position_counts", sa.JSON))


def downgrade() -> None:
    op.drop_column("oeil_summaries", "position_counts")
