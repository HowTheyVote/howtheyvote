"""Drop issues column

Revision ID: dab8b6d2b2fa
Revises: 61bc3894e172
Create Date: 2025-09-18 13:52:14.386407

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "dab8b6d2b2fa"
down_revision = "61bc3894e172"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("votes", "issues")


def downgrade() -> None:
    pass
