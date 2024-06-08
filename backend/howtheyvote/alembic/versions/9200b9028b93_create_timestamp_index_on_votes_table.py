"""create timestamp index on votes table

Revision ID: 9200b9028b93
Revises: 3eec8050f4d5
Create Date: 2024-05-06 15:49:49.074361

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "9200b9028b93"
down_revision = "3eec8050f4d5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_votes_timestamp", table_name="votes", columns=["timestamp"])


def downgrade() -> None:
    op.drop_index("ix_votes_timestamp", table_name="votes")
