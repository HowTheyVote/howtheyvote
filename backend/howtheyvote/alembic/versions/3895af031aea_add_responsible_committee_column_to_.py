"""Add responsible_committee column to votes table

Revision ID: 3895af031aea
Revises: 2f958a6f147d
Create Date: 2025-02-21 11:31:59.044124

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "3895af031aea"
down_revision = "2f958a6f147d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("votes", sa.Column("responsible_committee", sa.Unicode))


def downgrade() -> None:
    op.drop_column("votes", "responsible_committee")
