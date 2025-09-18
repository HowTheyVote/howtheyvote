"""Remove vote_groups table

Revision ID: ceeca4226a3e
Revises: dab8b6d2b2fa
Create Date: 2025-09-18 13:48:28.839598

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "ceeca4226a3e"
down_revision = "dab8b6d2b2fa"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table("vote_groups")


def downgrade() -> None:
    pass
