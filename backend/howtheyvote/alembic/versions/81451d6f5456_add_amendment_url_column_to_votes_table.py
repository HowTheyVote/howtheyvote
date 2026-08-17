"""Add amendment_url column to votes table

Revision ID: 81451d6f5456
Revises: 52476392fc07
Create Date: 2026-06-22 10:32:21.576588

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "81451d6f5456"
down_revision = "52476392fc07"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("votes", sa.Column("amendment_url", sa.Unicode))


def downgrade() -> None:
    op.drop_column("votes", "amendment_url")
