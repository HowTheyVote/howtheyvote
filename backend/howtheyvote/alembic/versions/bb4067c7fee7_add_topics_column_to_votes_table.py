"""Add topics column to votes table

Revision ID: bb4067c7fee7
Revises: 9e72d2f87fd9
Create Date: 2025-12-08 20:17:40.049670

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "bb4067c7fee7"
down_revision = "9e72d2f87fd9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("votes", sa.Column("topics", sa.JSON))


def downgrade() -> None:
    op.drop_column("votes", "topics")
