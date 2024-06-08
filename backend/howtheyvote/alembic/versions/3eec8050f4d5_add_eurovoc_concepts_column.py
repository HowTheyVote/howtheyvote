"""Add eurovoc_concepts column

Revision ID: 3eec8050f4d5
Revises: 9a4972f3a768
Create Date: 2024-03-31 17:25:34.058229

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "3eec8050f4d5"
down_revision = "9a4972f3a768"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("votes", sa.Column("eurovoc_concepts", sa.JSON))


def downgrade() -> None:
    op.drop_column("votes", "eurovoc_concepts")
