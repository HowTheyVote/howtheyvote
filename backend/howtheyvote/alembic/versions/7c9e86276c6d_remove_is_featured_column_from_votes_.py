"""Remove is_featured column from votes table

Revision ID: 7c9e86276c6d
Revises: 848ef24718dd
Create Date: 2025-03-14 22:46:51.712125

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "7c9e86276c6d"
down_revision = "848ef24718dd"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("votes", "is_featured")


def downgrade() -> None:
    op.add_column("votes", sa.Column("is_featured", sa.Boolean))
