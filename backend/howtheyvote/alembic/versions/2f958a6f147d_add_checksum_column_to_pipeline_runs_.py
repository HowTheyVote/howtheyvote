"""Add checksum column to pipeline_runs table

Revision ID: 2f958a6f147d
Revises: 1f516b18c4f6
Create Date: 2024-12-07 17:12:10.792707

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "2f958a6f147d"
down_revision = "1f516b18c4f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("pipeline_runs", sa.Column("checksum", sa.Unicode))


def downgrade() -> None:
    op.drop_column("pipeline_runs", "checksum")
