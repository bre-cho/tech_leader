"""P16 animation studio and karaoke subtitle engine

Revision ID: 20260429_0032
Revises: 20260429_0031
"""
from alembic import op
import sqlalchemy as sa

revision = "20260429_0032"
down_revision = "20260429_0031"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table("animation_projects",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("idea", sa.Text(), nullable=False),
        sa.Column("platform", sa.String(length=64), nullable=False, server_default="tiktok"),
        sa.Column("aspect_ratio", sa.String(length=16), nullable=False, server_default="9:16"),
        sa.Column("template_key", sa.String(length=128), nullable=False, server_default="news"),
        sa.Column("style_key", sa.String(length=128), nullable=False, server_default="cinematic_news"),
        sa.Column("voice_key", sa.String(length=128)),
        sa.Column("music_mood", sa.String(length=128)),
        sa.Column("status", sa.String(length=64), nullable=False, server_default="draft"),
        sa.Column("factory_run_id", sa.String()),
        sa.Column("render_job_id", sa.String()),
        sa.Column("final_video_url", sa.Text()),
        sa.Column("thumbnail_url", sa.Text()),
        sa.Column("qa_score", sa.Float()),
        sa.Column("qa_report", sa.JSON()),
        sa.Column("metadata_json", sa.JSON()),
        sa.Column("created_by", sa.String()),
        sa.Column("team_id", sa.String()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_animation_projects_status", "animation_projects", ["status"])
    op.create_index("ix_animation_projects_factory_run_id", "animation_projects", ["factory_run_id"])
    op.create_index("ix_animation_projects_render_job_id", "animation_projects", ["render_job_id"])

    op.create_table("animation_scenes",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("project_id", sa.String(), sa.ForeignKey("animation_projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("scene_index", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=512)),
        sa.Column("narration", sa.Text(), nullable=False),
        sa.Column("visual_prompt", sa.Text()),
        sa.Column("motion_prompt", sa.Text()),
        sa.Column("character_lock", sa.JSON()),
        sa.Column("duration_seconds", sa.Float(), nullable=False, server_default="5"),
        sa.Column("audio_url", sa.Text()),
        sa.Column("srt_url", sa.Text()),
        sa.Column("ass_url", sa.Text()),
        sa.Column("html_url", sa.Text()),
        sa.Column("video_url", sa.Text()),
        sa.Column("thumbnail_url", sa.Text()),
        sa.Column("status", sa.String(length=64), nullable=False, server_default="planned"),
        sa.Column("metadata_json", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_animation_scenes_project_scene", "animation_scenes", ["project_id", "scene_index"], unique=True)
    op.create_index("ix_animation_scenes_status", "animation_scenes", ["status"])

    op.create_table("animation_templates",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("key", sa.String(length=128), nullable=False, unique=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("default_style_key", sa.String(length=128), nullable=False),
        sa.Column("default_music_mood", sa.String(length=128)),
        sa.Column("scene_count_default", sa.Integer(), nullable=False, server_default="8"),
        sa.Column("prompt_contract", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("subtitle_contract", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("export_contract", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table("animation_style_presets",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("key", sa.String(length=128), nullable=False, unique=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("visual_language", sa.Text(), nullable=False),
        sa.Column("color_palette", sa.JSON()),
        sa.Column("typography", sa.JSON()),
        sa.Column("motion_rules", sa.JSON()),
        sa.Column("character_rules", sa.JSON()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table("export_presets",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("key", sa.String(length=128), nullable=False, unique=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("platform", sa.String(length=64), nullable=False),
        sa.Column("aspect_ratio", sa.String(length=16), nullable=False),
        sa.Column("width", sa.Integer(), nullable=False),
        sa.Column("height", sa.Integer(), nullable=False),
        sa.Column("fps", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("safe_zone", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("subtitle_style", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("render_settings", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

def downgrade() -> None:
    op.drop_table("export_presets")
    op.drop_table("animation_style_presets")
    op.drop_table("animation_templates")
    op.drop_table("animation_scenes")
    op.drop_table("animation_projects")
