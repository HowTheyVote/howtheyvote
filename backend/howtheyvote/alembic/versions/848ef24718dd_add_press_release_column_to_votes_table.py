"""Add press_release column to votes table

Revision ID: 848ef24718dd
Revises: 2fb74cc3d20c
Create Date: 2025-03-01 21:27:44.628151

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "848ef24718dd"
down_revision = "2fb74cc3d20c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("votes", sa.Column("press_release", sa.Unicode))


def downgrade() -> None:
    op.drop_column("votes", "press_release")
