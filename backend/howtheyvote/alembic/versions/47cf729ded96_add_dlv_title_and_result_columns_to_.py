"""Add dlv_title and result columns to votes table

Revision ID: 47cf729ded96
Revises: 7c9e86276c6d
Create Date: 2025-04-11 10:23:00.867950

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "47cf729ded96"
down_revision = "7c9e86276c6d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("votes", sa.Column("dlv_title", sa.Unicode))
    op.add_column("votes", sa.Column("result", sa.Unicode))


def downgrade() -> None:
    op.drop_column("votes", "dlv_title")
    op.drop_column("votes", "result")
