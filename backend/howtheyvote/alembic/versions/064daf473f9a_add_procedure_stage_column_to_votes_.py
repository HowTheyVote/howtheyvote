"""Add procedure_stage column to votes table

Revision ID: 064daf473f9a
Revises: 47cf729ded96
Create Date: 2025-04-11 14:53:28.949263

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "064daf473f9a"
down_revision = "47cf729ded96"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("votes", sa.Column("procedure_stage", sa.Unicode))


def downgrade() -> None:
    op.drop_column("votes", "procedure_stage")
