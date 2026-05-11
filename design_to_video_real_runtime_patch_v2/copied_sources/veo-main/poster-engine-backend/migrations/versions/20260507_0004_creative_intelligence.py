"""add creative intelligence tables

Revision ID: 20260507_0004
Revises: 20260505_0003
Create Date: 2026-05-07 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "20260507_0004"
down_revision = "20260505_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "creative_sessions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("owner_user_id", sa.String(), nullable=False),
        sa.Column("brand_id", sa.String(), nullable=True),
        sa.Column("industry", sa.String(), nullable=False),
        sa.Column("product", sa.String(), nullable=False),
        sa.Column("goal", sa.String(), nullable=False),
        sa.Column("platform", sa.String(), nullable=False),
        sa.Column("audience", sa.String(), nullable=False),
        sa.Column("perception_targets", sa.JSON(), nullable=False),
        sa.Column("assets", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["brand_id"], ["brands.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_creative_sessions_owner_user_id", "creative_sessions", ["owner_user_id"])
    op.create_index("ix_creative_sessions_brand_id", "creative_sessions", ["brand_id"])
    op.create_index("ix_creative_sessions_industry", "creative_sessions", ["industry"])

    op.create_table(
        "creative_plans",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["creative_sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_creative_plans_session_id", "creative_plans", ["session_id"])

    op.create_table(
        "creative_poster_scores",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("ctr_score", sa.Float(), nullable=False),
        sa.Column("luxury_score", sa.Float(), nullable=False),
        sa.Column("readability_score", sa.Float(), nullable=False),
        sa.Column("brand_recall_score", sa.Float(), nullable=False),
        sa.Column("emotional_score", sa.Float(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["creative_sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_creative_poster_scores_session_id", "creative_poster_scores", ["session_id"])

    op.create_table(
        "brand_dna",
        sa.Column("brand_id", sa.String(), nullable=False),
        sa.Column("dna", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["brand_id"], ["brands.id"]),
        sa.PrimaryKeyConstraint("brand_id"),
    )

    op.create_table(
        "creative_render_jobs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("session_id", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("result", sa.JSON(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["creative_sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_creative_render_jobs_session_id", "creative_render_jobs", ["session_id"])
    op.create_index("ix_creative_render_jobs_status", "creative_render_jobs", ["status"])


def downgrade() -> None:
    op.drop_index("ix_creative_render_jobs_status", table_name="creative_render_jobs")
    op.drop_index("ix_creative_render_jobs_session_id", table_name="creative_render_jobs")
    op.drop_table("creative_render_jobs")
    op.drop_table("brand_dna")
    op.drop_index("ix_creative_poster_scores_session_id", table_name="creative_poster_scores")
    op.drop_table("creative_poster_scores")
    op.drop_index("ix_creative_plans_session_id", table_name="creative_plans")
    op.drop_table("creative_plans")
    op.drop_index("ix_creative_sessions_industry", table_name="creative_sessions")
    op.drop_index("ix_creative_sessions_brand_id", table_name="creative_sessions")
    op.drop_index("ix_creative_sessions_owner_user_id", table_name="creative_sessions")
    op.drop_table("creative_sessions")