"""Add drama ML label tables for tension, intent, subtext and memory-recall trainers.

Revision ID: 20260505_0033
Revises: 20260429_0032
"""
from alembic import op
import sqlalchemy as sa

revision = "20260505_0033"
down_revision = "20260429_0032"
branch_labels = None
depends_on = None

# Common timestamp columns reused across all four label tables.
_TIMESTAMP_COLS = [
    sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
    sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
    sa.Column("source", sa.String(64), nullable=False, server_default="heuristic"),
]


def upgrade() -> None:
    # -----------------------------------------------------------------------
    # 1. drama_scene_tension_labels
    # -----------------------------------------------------------------------
    op.create_table(
        "drama_scene_tension_labels",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("scene_id", sa.String(255), nullable=False, index=True),
        # Feature columns (must match drama_tension_trainer._FEATURE_COLUMNS)
        sa.Column("intent_count", sa.Float(), nullable=False, server_default="0"),
        sa.Column("relationship_count", sa.Float(), nullable=False, server_default="0"),
        sa.Column("hidden_agenda_sum", sa.Float(), nullable=False, server_default="0"),
        sa.Column("dominance_sum", sa.Float(), nullable=False, server_default="0"),
        sa.Column("exposure_risk", sa.Float(), nullable=False, server_default="0"),
        sa.Column("unresolved_prior_memory", sa.Float(), nullable=False, server_default="0"),
        sa.Column("time_pressure", sa.Float(), nullable=False, server_default="0"),
        sa.Column("social_consequence", sa.Float(), nullable=False, server_default="0"),
        # Label column: ∈ [0, 100] (trainer rescales to [0, 1])
        sa.Column("tension_score_label", sa.Float(), nullable=True),
        *_TIMESTAMP_COLS,
    )
    op.create_index(
        "ix_drama_tension_labels_created_at",
        "drama_scene_tension_labels",
        ["created_at"],
    )

    # -----------------------------------------------------------------------
    # 2. drama_scene_intent_labels
    # -----------------------------------------------------------------------
    op.create_table(
        "drama_scene_intent_labels",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("scene_id", sa.String(255), nullable=False, index=True),
        sa.Column("character_id", sa.String(255), nullable=True, index=True),
        # Feature columns (must match drama_character_intent_trainer._FEATURE_COLUMNS)
        sa.Column("dominance_delta", sa.Float(), nullable=False, server_default="0"),
        sa.Column("hidden_agenda_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("goal_urgency", sa.Float(), nullable=False, server_default="0"),
        sa.Column("emotional_state_valence", sa.Float(), nullable=False, server_default="0"),
        sa.Column("relationship_tension", sa.Float(), nullable=False, server_default="0"),
        sa.Column("scene_power_shift", sa.Float(), nullable=False, server_default="0"),
        # Multi-label: one column per intent class (binary 0/1)
        sa.Column("label_reveal", sa.SmallInteger(), nullable=True),
        sa.Column("label_manipulate", sa.SmallInteger(), nullable=True),
        sa.Column("label_deflect", sa.SmallInteger(), nullable=True),
        sa.Column("label_escalate", sa.SmallInteger(), nullable=True),
        sa.Column("label_appease", sa.SmallInteger(), nullable=True),
        sa.Column("label_pursue", sa.SmallInteger(), nullable=True),
        *_TIMESTAMP_COLS,
    )
    op.create_index(
        "ix_drama_intent_labels_created_at",
        "drama_scene_intent_labels",
        ["created_at"],
    )

    # -----------------------------------------------------------------------
    # 3. drama_scene_subtext_labels
    # -----------------------------------------------------------------------
    op.create_table(
        "drama_scene_subtext_labels",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("scene_id", sa.String(255), nullable=False, index=True),
        sa.Column("character_id", sa.String(255), nullable=True, index=True),
        # Feature columns (must match drama_subtext_trainer._FEATURE_COLUMNS)
        sa.Column("dominance_delta", sa.Float(), nullable=False, server_default="0"),
        sa.Column("hidden_agenda_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("goal_urgency", sa.Float(), nullable=False, server_default="0"),
        sa.Column("emotional_state_valence", sa.Float(), nullable=False, server_default="0"),
        sa.Column("relationship_tension", sa.Float(), nullable=False, server_default="0"),
        sa.Column("power_shift_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("memory_recall_weight", sa.Float(), nullable=False, server_default="0"),
        # Multi-label: one column per subtext class (binary 0/1)
        sa.Column("label_denial", sa.SmallInteger(), nullable=True),
        sa.Column("label_deflection", sa.SmallInteger(), nullable=True),
        sa.Column("label_sarcasm", sa.SmallInteger(), nullable=True),
        sa.Column("label_suppression", sa.SmallInteger(), nullable=True),
        sa.Column("label_vulnerability", sa.SmallInteger(), nullable=True),
        *_TIMESTAMP_COLS,
    )
    op.create_index(
        "ix_drama_subtext_labels_created_at",
        "drama_scene_subtext_labels",
        ["created_at"],
    )

    # -----------------------------------------------------------------------
    # 4. drama_scene_memory_recall_labels
    # -----------------------------------------------------------------------
    op.create_table(
        "drama_scene_memory_recall_labels",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("scene_id", sa.String(255), nullable=False, index=True),
        sa.Column("character_id", sa.String(255), nullable=True, index=True),
        # Feature columns (must match drama_memory_recall_trainer._FEATURE_COLUMNS)
        sa.Column("trigger_word_match_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("emotional_weight", sa.Float(), nullable=False, server_default="0"),
        sa.Column("time_since_event_days", sa.Float(), nullable=False, server_default="0"),
        sa.Column("relationship_intensity", sa.Float(), nullable=False, server_default="0"),
        sa.Column("persistence_weight", sa.Float(), nullable=False, server_default="0"),
        sa.Column("prior_activation_count", sa.Float(), nullable=False, server_default="0"),
        # Label: recall score ∈ [0, 1]
        sa.Column("recall_score_label", sa.Float(), nullable=True),
        *_TIMESTAMP_COLS,
    )
    op.create_index(
        "ix_drama_memory_recall_labels_created_at",
        "drama_scene_memory_recall_labels",
        ["created_at"],
    )


def downgrade() -> None:
    op.drop_table("drama_scene_memory_recall_labels")
    op.drop_table("drama_scene_subtext_labels")
    op.drop_table("drama_scene_intent_labels")
    op.drop_table("drama_scene_tension_labels")
