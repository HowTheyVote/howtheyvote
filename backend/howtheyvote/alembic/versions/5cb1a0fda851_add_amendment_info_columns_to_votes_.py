"""Add amendment info columns to votes table

Revision ID: 5cb1a0fda851
Revises: ceeca4226a3e
Create Date: 2025-05-01 20:46:37.457523

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "5cb1a0fda851"
down_revision = "ceeca4226a3e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("votes", sa.Column("amendment_subject", sa.Unicode))
    op.add_column("votes", sa.Column("amendment_number", sa.Unicode))
    op.add_column("votes", sa.Column("amendment_authors", sa.JSON))


def downgrade() -> None:
    op.drop_column("votes", "amendment_subject")
    op.drop_column("votes", "amendment_number")
    op.drop_column("votes", "amendment_authors")
