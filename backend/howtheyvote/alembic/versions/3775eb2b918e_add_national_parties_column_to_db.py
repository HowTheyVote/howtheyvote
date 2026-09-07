"""add national parties column to db

Revision ID: 3775eb2b918e
Revises: 52476392fc07
Create Date: 2026-08-03 15:16:41.197339

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "3775eb2b918e"
down_revision = "52476392fc07"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("members", sa.Column("national_party_memberships", sa.JSON))


def downgrade() -> None:
    op.drop_column("members", "national_party_memberships")
