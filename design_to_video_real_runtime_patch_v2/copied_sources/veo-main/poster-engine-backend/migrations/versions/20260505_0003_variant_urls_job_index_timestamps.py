"""add variant urls, job index, brand/project updated_at

Revision ID: 20260505_0003
Revises: 20260505_0002
Create Date: 2026-05-05 01:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260505_0003"
down_revision = "20260505_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # P4 – Store real provider image/export URLs on poster variants.
    op.add_column("poster_variants", sa.Column("image_url", sa.String(), nullable=True))
    op.add_column("poster_variants", sa.Column("export_url", sa.String(), nullable=True))

    # P9 – Index for jobs.project_id to support future per-project job queries.
    op.create_index("ix_jobs_project_id", "jobs", ["project_id"])

    # P12 – Track last-modified timestamps for brands and projects.
    op.add_column("brands", sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("projects", sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("projects", "updated_at")
    op.drop_column("brands", "updated_at")
    op.drop_index("ix_jobs_project_id", table_name="jobs")
    op.drop_column("poster_variants", "export_url")
    op.drop_column("poster_variants", "image_url")
