"""Add kill_switch_flags table for DB-backed flag persistence (P1.3).

Revision ID: 20260505_0034
Revises: 20260505_0033
"""
from alembic import op
import sqlalchemy as sa

revision = "20260505_0034"
down_revision = "20260505_0033"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "kill_switch_flags",
        sa.Column("feature_name", sa.String(255), primary_key=True, nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index(
        "ix_kill_switch_flags_updated_at",
        "kill_switch_flags",
        ["updated_at"],
    )


def downgrade() -> None:
    op.drop_table("kill_switch_flags")
