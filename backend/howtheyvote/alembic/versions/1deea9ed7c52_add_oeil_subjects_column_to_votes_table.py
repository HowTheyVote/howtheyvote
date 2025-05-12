"""Add oeil_subjects column to votes table

Revision ID: 1deea9ed7c52
Revises: 8d1995cb0bed
Create Date: 2025-05-11 20:30:46.675280

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1deea9ed7c52"
down_revision = "8d1995cb0bed"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("votes", sa.Column("oeil_subjects", sa.JSON))


def downgrade() -> None:
    op.drop_column("votes", "oeil_subjects")
