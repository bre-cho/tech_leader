"""baseline runtime tables

Revision ID: 20260514_01
Revises:
Create Date: 2026-05-14 22:45:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260514_01"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "workflow_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("workflow_id", sa.String(length=80), nullable=False),
        sa.Column("workflow_name", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("input_json", sa.Text(), nullable=False),
        sa.Column("output_json", sa.Text(), nullable=True),
        sa.Column("verification_json", sa.Text(), nullable=True),
        sa.Column("promotion_status", sa.String(length=80), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_workflow_runs_workflow_id", "workflow_runs", ["workflow_id"])
    op.create_index("ix_workflow_runs_workflow_name", "workflow_runs", ["workflow_name"])
    op.create_index("ix_workflow_runs_status", "workflow_runs", ["status"])

    op.create_table(
        "winner_dna",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("industry", sa.String(length=120), nullable=False),
        sa.Column("visual_type", sa.String(length=120), nullable=False),
        sa.Column("hook", sa.Text(), nullable=False),
        sa.Column("offer", sa.Text(), nullable=False),
        sa.Column("conversion_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("upsell_rate", sa.Float(), nullable=False, server_default="0"),
        sa.Column("storyboard_pattern", sa.Text(), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_winner_dna_industry", "winner_dna", ["industry"])

    op.create_table(
        "context_entities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("entity_type", sa.String(length=120), nullable=False),
        sa.Column("entity_key", sa.String(length=240), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint("entity_key", name="uq_context_entities_entity_key"),
    )
    op.create_index("ix_context_entities_entity_type", "context_entities", ["entity_type"])
    op.create_index("ix_context_entities_entity_key", "context_entities", ["entity_key"])

    op.create_table(
        "context_relations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_key", sa.String(length=240), nullable=False),
        sa.Column("relation_type", sa.String(length=120), nullable=False),
        sa.Column("target_key", sa.String(length=240), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint("source_key", "relation_type", "target_key", name="uq_context_relations_triplet"),
    )
    op.create_index("ix_context_relations_source_key", "context_relations", ["source_key"])
    op.create_index("ix_context_relations_relation_type", "context_relations", ["relation_type"])
    op.create_index("ix_context_relations_target_key", "context_relations", ["target_key"])

    op.create_table(
        "agent_trust",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("agent_name", sa.String(length=120), nullable=False),
        sa.Column("trust_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("sample_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint("agent_name", name="uq_agent_trust_agent_name"),
    )
    op.create_index("ix_agent_trust_agent_name", "agent_trust", ["agent_name"])

    op.create_table(
        "replay_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("snapshot_id", sa.String(length=120), nullable=False),
        sa.Column("workflow_id", sa.String(length=80), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("output_hash", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint("snapshot_id", name="uq_replay_snapshots_snapshot_id"),
    )
    op.create_index("ix_replay_snapshots_snapshot_id", "replay_snapshots", ["snapshot_id"])
    op.create_index("ix_replay_snapshots_workflow_id", "replay_snapshots", ["workflow_id"])
    op.create_index("ix_replay_snapshots_output_hash", "replay_snapshots", ["output_hash"])


def downgrade() -> None:
    op.drop_index("ix_replay_snapshots_output_hash", table_name="replay_snapshots")
    op.drop_index("ix_replay_snapshots_workflow_id", table_name="replay_snapshots")
    op.drop_index("ix_replay_snapshots_snapshot_id", table_name="replay_snapshots")
    op.drop_table("replay_snapshots")
    op.drop_index("ix_agent_trust_agent_name", table_name="agent_trust")
    op.drop_table("agent_trust")
    op.drop_index("ix_context_relations_target_key", table_name="context_relations")
    op.drop_index("ix_context_relations_relation_type", table_name="context_relations")
    op.drop_index("ix_context_relations_source_key", table_name="context_relations")
    op.drop_table("context_relations")
    op.drop_index("ix_context_entities_entity_key", table_name="context_entities")
    op.drop_index("ix_context_entities_entity_type", table_name="context_entities")
    op.drop_table("context_entities")
    op.drop_index("ix_winner_dna_industry", table_name="winner_dna")
    op.drop_table("winner_dna")
    op.drop_index("ix_workflow_runs_status", table_name="workflow_runs")
    op.drop_index("ix_workflow_runs_workflow_name", table_name="workflow_runs")
    op.drop_index("ix_workflow_runs_workflow_id", table_name="workflow_runs")
    op.drop_table("workflow_runs")
