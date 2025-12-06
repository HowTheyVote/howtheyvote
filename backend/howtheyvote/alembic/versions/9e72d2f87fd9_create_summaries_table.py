"""create summaries table

Revision ID: 9e72d2f87fd9
Revises: 93de5ba071f5
Create Date: 2025-11-17 20:57:09.060893

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "9e72d2f87fd9"
down_revision = "93de5ba071f5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "summaries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("content", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("summaries")
