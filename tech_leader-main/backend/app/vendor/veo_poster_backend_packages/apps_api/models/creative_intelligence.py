import uuid

from sqlalchemy import DateTime, Float, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from apps.api.db.session import Base


def _uid() -> str:
    return str(uuid.uuid4())


class CreativeSession(Base):
    __tablename__ = "creative_sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uid)
    owner_user_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    brand_id: Mapped[str | None] = mapped_column(String, ForeignKey("brands.id"), nullable=True, index=True)
    industry: Mapped[str] = mapped_column(String, nullable=False, index=True)
    product: Mapped[str] = mapped_column(String, nullable=False)
    goal: Mapped[str] = mapped_column(String, nullable=False)
    platform: Mapped[str] = mapped_column(String, nullable=False)
    audience: Mapped[str] = mapped_column(String, nullable=False)
    perception_targets: Mapped[list] = mapped_column(JSON, default=list)
    assets: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CreativePlan(Base):
    __tablename__ = "creative_plans"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uid)
    session_id: Mapped[str] = mapped_column(String, ForeignKey("creative_sessions.id"), nullable=False, index=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PosterScore(Base):
    __tablename__ = "creative_poster_scores"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uid)
    session_id: Mapped[str] = mapped_column(String, ForeignKey("creative_sessions.id"), nullable=False, index=True)
    ctr_score: Mapped[float] = mapped_column(Float, nullable=False)
    luxury_score: Mapped[float] = mapped_column(Float, nullable=False)
    readability_score: Mapped[float] = mapped_column(Float, nullable=False)
    brand_recall_score: Mapped[float] = mapped_column(Float, nullable=False)
    emotional_score: Mapped[float] = mapped_column(Float, nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())


class BrandDNA(Base):
    __tablename__ = "brand_dna"

    brand_id: Mapped[str] = mapped_column(String, ForeignKey("brands.id"), primary_key=True)
    dna: Mapped[dict] = mapped_column(JSON, nullable=False)
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class CreativeRenderJob(Base):
    __tablename__ = "creative_render_jobs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uid)
    session_id: Mapped[str | None] = mapped_column(String, ForeignKey("creative_sessions.id"), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String, nullable=False, default="queued", index=True)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    provider: Mapped[str] = mapped_column(String, nullable=False, default="mock")
    result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
