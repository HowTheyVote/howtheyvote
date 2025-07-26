"""Add texts_adopted_reference column to votes table

Revision ID: 61bc3894e172
Revises: 184528e5ba14
Create Date: 2025-07-26 13:04:43.332266

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "61bc3894e172"
down_revision = "184528e5ba14"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("votes", sa.Column("texts_adopted_reference", sa.Unicode))


def downgrade() -> None:
    op.drop_column("votes", "texts_adopted_reference")
