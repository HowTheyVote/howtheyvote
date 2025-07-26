"""Add idempotency key to pipeline_runs table

Revision ID: 184528e5ba14
Revises: 1deea9ed7c52
Create Date: 2025-07-11 15:13:37.330203

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "184528e5ba14"
down_revision = "1deea9ed7c52"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("pipeline_runs", sa.Column("idempotency_key", sa.Unicode))


def downgrade() -> None:
    op.drop_column("pipeline_runs", "idempotency_key")
