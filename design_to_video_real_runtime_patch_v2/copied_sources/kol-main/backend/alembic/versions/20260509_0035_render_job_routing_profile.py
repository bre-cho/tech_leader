"""Add routing_profile column to render_jobs for learning-loop fidelity.

Revision ID: 20260509_0035
Revises: 20260505_0034
"""
from alembic import op
import sqlalchemy as sa

revision = "20260509_0035"
down_revision = "20260505_0034"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "render_jobs",
        sa.Column(
            "routing_profile",
            sa.String(length=64),
            nullable=False,
            server_default="cinematic_ads",
        ),
    )


def downgrade() -> None:
    op.drop_column("render_jobs", "routing_profile")
