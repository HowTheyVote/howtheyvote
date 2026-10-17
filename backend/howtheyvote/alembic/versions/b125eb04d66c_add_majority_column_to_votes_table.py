"""add majority column to votes table

Revision ID: b125eb04d66c
Revises: 3775eb2b918e
Create Date: 2026-10-17 16:39:02.538825

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "b125eb04d66c"
down_revision = "3775eb2b918e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("votes", sa.Column("majority_type", sa.Unicode))


def downgrade() -> None:
    op.drop_column("votes", "majority_type")
