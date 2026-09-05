"""Add keywords column to votes table

Revision ID: af1689d1ec9f
Revises: 52476392fc07
Create Date: 2026-07-12 18:13:29.276452

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "af1689d1ec9f"
down_revision = "52476392fc07"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("votes", sa.Column("keywords", sa.JSON))


def downgrade() -> None:
    op.drop_column("votes", "keywords")
