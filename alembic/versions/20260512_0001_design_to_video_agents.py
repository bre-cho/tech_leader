"""design to video multi-agent schema

Revision ID: 20260512_0001
Revises: 
Create Date: 2026-05-12
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260512_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("design_projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("industry", sa.String(120), nullable=False),
        sa.Column("product", sa.String(255), nullable=False),
        sa.Column("goal", sa.String(120), nullable=False, server_default="sales"),
        sa.Column("channel", sa.String(120), nullable=False, server_default="Facebook"),
        sa.Column("status", sa.String(80), nullable=False, server_default="created"),
        sa.Column("input_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table("image_variants",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("concept_name", sa.String(255), nullable=False),
        sa.Column("headline", sa.String(255)),
        sa.Column("cta", sa.String(255)),
        sa.Column("visual_prompt", sa.Text(), nullable=False),
        sa.Column("image_url", sa.Text()),
        sa.Column("selected", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table("image_scores",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("image_variant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("attention_score", sa.Float(), nullable=False),
        sa.Column("trust_score", sa.Float(), nullable=False),
        sa.Column("conversion_score", sa.Float(), nullable=False),
        sa.Column("brand_fit_score", sa.Float(), nullable=False),
        sa.Column("upsell_video_potential_score", sa.Float(), nullable=False),
        sa.Column("video_upsell_ready", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("raw", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table("agent_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agent_name", sa.String(120), nullable=False),
        sa.Column("trace_id", sa.String(120), nullable=False),
        sa.Column("input_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("output_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("confidence_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("decision_reason", sa.Text()),
        sa.Column("lineage", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_agent_runs_trace_id", "agent_runs", ["trace_id"])
    op.create_table("winner_dna",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("industry", sa.String(120), nullable=False),
        sa.Column("style", sa.String(255)),
        sa.Column("hook", sa.Text()),
        sa.Column("offer", sa.Text()),
        sa.Column("score_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("why_this_won", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("winner_dna")
    op.drop_index("ix_agent_runs_trace_id", table_name="agent_runs")
    op.drop_table("agent_runs")
    op.drop_table("image_scores")
    op.drop_table("image_variants")
    op.drop_table("design_projects")
