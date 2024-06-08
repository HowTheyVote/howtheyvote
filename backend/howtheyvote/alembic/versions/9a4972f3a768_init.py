"""Init

Revision ID: 9a4972f3a768
Revises:
Create Date: 2024-03-29 16:46:24.464882

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "9a4972f3a768"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "fragments",
        sa.Column("model", sa.Unicode, nullable=False),
        sa.Column("source_name", sa.Unicode, nullable=False),
        sa.Column("source_id", sa.Unicode, nullable=False),
        sa.Column("source_url", sa.Unicode, nullable=True),
        sa.Column("timestamp", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("group_key", sa.Unicode, nullable=False),
        sa.Column("data", sa.JSON, nullable=False),
        sa.PrimaryKeyConstraint("model", "source_name", "source_id", name="pk_fragment"),
    )

    op.create_index("ix_fragments_group_key", "fragments", ["group_key"])

    op.create_table(
        "members",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("first_name", sa.Unicode),
        sa.Column("last_name", sa.Unicode),
        sa.Column("country", sa.Unicode),
        sa.Column("terms", sa.JSON),
        sa.Column("group_memberships", sa.JSON),
        sa.Column("date_of_birth", sa.Date),
        sa.Column("email", sa.Unicode),
        sa.Column("facebook", sa.Unicode),
        sa.Column("twitter", sa.Unicode),
    )

    op.create_table(
        "plenary_sessions",
        sa.Column("id", sa.Unicode, primary_key=True),
        sa.Column("term", sa.Integer),
        sa.Column("start_date", sa.Date),
        sa.Column("end_date", sa.Date),
        sa.Column("location", sa.Unicode),
    )

    op.create_table(
        "votes",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("timestamp", sa.DateTime),
        sa.Column("order", sa.Integer),
        sa.Column("title", sa.Unicode),
        sa.Column("reference", sa.Unicode),
        sa.Column("rapporteur", sa.Unicode),
        sa.Column("description", sa.Unicode),
        sa.Column("procedure_title", sa.Unicode),
        sa.Column("procedure_reference", sa.Unicode),
        sa.Column("geo_areas", sa.JSON),
        sa.Column("is_main", sa.Boolean),
        sa.Column("is_featured", sa.Boolean),
        sa.Column("group_key", sa.Unicode),
        sa.Column("member_votes", sa.JSON),
        sa.Column("issues", sa.JSON),
    )

    op.create_table(
        "vote_groups",
        sa.Column("id", sa.Unicode, primary_key=True),
        sa.Column("date", sa.Date),
        sa.Column("issues", sa.JSON),
    )

    op.create_table(
        "press_releases",
        sa.Column("id", sa.Unicode, primary_key=True),
        sa.Column("published_at", sa.DateTime),
        sa.Column("term", sa.Integer),
        sa.Column("title", sa.Unicode),
        sa.Column("references", sa.JSON),
        sa.Column("procedure_references", sa.JSON),
        sa.Column("facts", sa.Unicode),
    )

    op.create_table(
        "pipeline_runs",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("pipeline", sa.Unicode, nullable=False),
        sa.Column("started_at", sa.DateTime, nullable=False),
        sa.Column("finished_at", sa.DateTime, nullable=False),
        sa.Column("result", sa.Unicode, nullable=False),
    )

    op.create_index(
        "ix_pipeline_runs_pipeline_result", "pipeline_runs", ["pipeline", "result"]
    )


def downgrade() -> None:
    pass
