"""Rename result column to status

Revision ID: 1f516b18c4f6
Revises: 9b35d19b64c4
Create Date: 2024-12-08 11:25:26.051408

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "1f516b18c4f6"
down_revision = "9b35d19b64c4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("pipeline_runs", column_name="result", new_column_name="status")


def downgrade() -> None:
    op.alter_column("pipeline_runs", column_name="status", new_column_name="result")
