"""Make responsible_committee column JSON in votes table

Revision ID: 8d1995cb0bed
Revises: 064daf473f9a
Create Date: 2025-03-16 17:13:08.000602

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "8d1995cb0bed"
down_revision = "064daf473f9a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("votes", "responsible_committee")
    op.add_column("votes", sa.Column("responsible_committees", sa.JSON))


def downgrade() -> None:
    op.drop_column("votes", "responsible_committees")
    op.add_column("votes", sa.Column("responsible_committee", sa.Unicode))
