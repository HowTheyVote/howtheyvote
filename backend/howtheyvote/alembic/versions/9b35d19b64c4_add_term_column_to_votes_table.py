"""add term column to votes table

Revision ID: 9b35d19b64c4
Revises: 9200b9028b93
Create Date: 2024-08-06 18:52:06.033551

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "9b35d19b64c4"
down_revision = "9200b9028b93"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("votes", sa.Column("term", sa.Integer))
    op.create_index("ix_votes_term", table_name="votes", columns=["term"])


def downgrade() -> None:
    op.drop_column("votes", "term")
    op.drop_index("ix_votes_term", table_name="votes")
