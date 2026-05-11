from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()


class DesignProject(Base):
    __tablename__ = "design_projects"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), nullable=True)
    industry = Column(String(120), nullable=False)
    product = Column(String(255), nullable=False)
    goal = Column(String(120), nullable=False, default="sales")
    channel = Column(String(120), nullable=False, default="Facebook")
    status = Column(String(80), nullable=False, default="created")
    input_payload = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ImageVariant(Base):
    __tablename__ = "image_variants"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("design_projects.id"), nullable=False)
    concept_name = Column(String(255), nullable=False)
    headline = Column(String(255), nullable=True)
    cta = Column(String(255), nullable=True)
    visual_prompt = Column(Text, nullable=False)
    image_url = Column(Text, nullable=True)
    selected = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ImageScore(Base):
    __tablename__ = "image_scores"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    image_variant_id = Column(UUID(as_uuid=True), ForeignKey("image_variants.id"), nullable=False)
    attention_score = Column(Float, nullable=False)
    trust_score = Column(Float, nullable=False)
    conversion_score = Column(Float, nullable=False)
    brand_fit_score = Column(Float, nullable=False)
    upsell_video_potential_score = Column(Float, nullable=False)
    video_upsell_ready = Column(Boolean, nullable=False, default=False)
    raw = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AgentRun(Base):
    __tablename__ = "agent_runs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=False)
    agent_name = Column(String(120), nullable=False)
    trace_id = Column(String(120), nullable=False, index=True)
    input_payload = Column(JSON, nullable=False, default=dict)
    output_payload = Column(JSON, nullable=False, default=dict)
    confidence_score = Column(Float, nullable=False, default=0)
    decision_reason = Column(Text, nullable=True)
    lineage = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class WinnerDNA(Base):
    __tablename__ = "winner_dna"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=False)
    industry = Column(String(120), nullable=False)
    style = Column(String(255), nullable=True)
    hook = Column(Text, nullable=True)
    offer = Column(Text, nullable=True)
    score_snapshot = Column(JSON, nullable=False, default=dict)
    why_this_won = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
