"""Rename amendment_url column

Revision ID: c3cda7836f98
Revises: 81451d6f5456
Create Date: 2026-08-12 17:40:17.022304

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c3cda7836f98"
down_revision = "81451d6f5456"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("votes", "amendment_url")
    op.add_column("votes", sa.Column("amendment_urls", sa.JSON))


def downgrade() -> None:
    op.drop_column("votes", "amendment_urls")
    op.add_column("votes", sa.Column("amendment_url", sa.Unicode))
