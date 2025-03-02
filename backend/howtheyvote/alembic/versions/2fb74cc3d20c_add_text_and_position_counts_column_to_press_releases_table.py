"""Add text and position_counts column to press_releases table

Revision ID: 2fb74cc3d20c
Revises: 3895af031aea
Create Date: 2025-02-23 13:13:56.054579

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "2fb74cc3d20c"
down_revision = "3895af031aea"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("press_releases", sa.Column("text", sa.Unicode))
    op.add_column("press_releases", sa.Column("position_counts", sa.JSON))


def downgrade() -> None:
    op.drop_column("press_releases", "text")
    op.drop_column("press_releases", "position_counts")
