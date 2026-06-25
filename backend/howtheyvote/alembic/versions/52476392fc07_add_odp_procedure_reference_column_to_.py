"""Add odp_procedure_reference column to votes table

Revision ID: 52476392fc07
Revises: 6ad570082ec0
Create Date: 2026-06-17 13:44:33.900092

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "52476392fc07"
down_revision = "6ad570082ec0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("votes", sa.Column("odp_procedure_reference", sa.Unicode))


def downgrade() -> None:
    op.drop_column("votes", "odp_procedure_reference")
