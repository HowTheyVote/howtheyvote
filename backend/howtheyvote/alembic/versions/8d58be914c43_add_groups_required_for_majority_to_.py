"""add groups_required_for_majority to votes table

Revision ID: 8d58be914c43
Revises: b125eb04d66c
Create Date: 2026-10-17 16:58:46.043099

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "8d58be914c43"
down_revision = "b125eb04d66c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("votes", sa.Column("groups_required_for_majority", sa.JSON))


def downgrade() -> None:
    op.drop_column("votes", "groups_required_for_majority")
