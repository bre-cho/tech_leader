"""audit framework tables

Revision ID: 20260514_02
Revises: 20260514_01
Create Date: 2026-05-14 23:30:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260514_02"
down_revision: Union[str, None] = "20260514_01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # P0-002 — add input_hash + runtime_version to replay_snapshots
    op.add_column("replay_snapshots", sa.Column("input_hash", sa.String(length=128), nullable=True))
    op.add_column("replay_snapshots", sa.Column("runtime_version", sa.String(length=40), nullable=True))
    op.create_index("ix_replay_snapshots_input_hash", "replay_snapshots", ["input_hash"])

    # P1-002 — state propagation log
    op.create_table(
        "state_propagation_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("workflow_id", sa.String(length=80), nullable=False),
        sa.Column("source_agent", sa.String(length=120), nullable=False),
        sa.Column("target_agent", sa.String(length=120), nullable=False),
        sa.Column("state_key", sa.String(length=240), nullable=False),
        sa.Column("value_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_state_propagation_workflow_id", "state_propagation_log", ["workflow_id"])
    op.create_index("ix_state_propagation_source_agent", "state_propagation_log", ["source_agent"])
    op.create_index("ix_state_propagation_target_agent", "state_propagation_log", ["target_agent"])

    # P1-003 — retry state
    op.create_table(
        "retry_state",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("workflow_id", sa.String(length=80), nullable=False),
        sa.Column("agent_name", sa.String(length=120), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("last_status", sa.String(length=40), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint("idempotency_key", name="uq_retry_state_idempotency_key"),
    )
    op.create_index("ix_retry_state_idempotency_key", "retry_state", ["idempotency_key"])
    op.create_index("ix_retry_state_workflow_id", "retry_state", ["workflow_id"])

    # P1-004 — decision log
    op.create_table(
        "decision_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("decision_id", sa.String(length=80), nullable=False),
        sa.Column("workflow_id", sa.String(length=80), nullable=False),
        sa.Column("decision_type", sa.String(length=120), nullable=False),
        sa.Column("outcome", sa.String(length=40), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint("decision_id", name="uq_decision_log_decision_id"),
    )
    op.create_index("ix_decision_log_decision_id", "decision_log", ["decision_id"])
    op.create_index("ix_decision_log_workflow_id", "decision_log", ["workflow_id"])
    op.create_index("ix_decision_log_decision_type", "decision_log", ["decision_type"])
    op.create_index("ix_decision_log_outcome", "decision_log", ["outcome"])


def downgrade() -> None:
    op.drop_index("ix_decision_log_outcome", table_name="decision_log")
    op.drop_index("ix_decision_log_decision_type", table_name="decision_log")
    op.drop_index("ix_decision_log_workflow_id", table_name="decision_log")
    op.drop_index("ix_decision_log_decision_id", table_name="decision_log")
    op.drop_table("decision_log")

    op.drop_index("ix_retry_state_workflow_id", table_name="retry_state")
    op.drop_index("ix_retry_state_idempotency_key", table_name="retry_state")
    op.drop_table("retry_state")

    op.drop_index("ix_state_propagation_target_agent", table_name="state_propagation_log")
    op.drop_index("ix_state_propagation_source_agent", table_name="state_propagation_log")
    op.drop_index("ix_state_propagation_workflow_id", table_name="state_propagation_log")
    op.drop_table("state_propagation_log")

    op.drop_index("ix_replay_snapshots_input_hash", table_name="replay_snapshots")
    op.drop_column("replay_snapshots", "runtime_version")
    op.drop_column("replay_snapshots", "input_hash")
