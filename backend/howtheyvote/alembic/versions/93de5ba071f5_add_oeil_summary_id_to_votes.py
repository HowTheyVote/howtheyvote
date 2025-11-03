"""add oeil_summary_id to votes

Revision ID: 93de5ba071f5
Revises: b8621d92d68c
Create Date: 2025-11-03 19:29:23.421529

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '93de5ba071f5'
down_revision = 'b8621d92d68c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("votes", sa.Column("oeil_summary_id", sa.Integer))

def downgrade() -> None:
    op.drop_column("votes", "oeil_summary_id")
