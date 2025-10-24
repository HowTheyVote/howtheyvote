"""Rename press_release column

Revision ID: b8621d92d68c
Revises: 5cb1a0fda851
Create Date: 2025-10-17 13:35:38.346785

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "b8621d92d68c"
down_revision = "5cb1a0fda851"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("votes", "press_release", new_column_name="press_release_id")


def downgrade() -> None:
    op.alter_column("votes", "press_release_id", new_column_name="press_release")
