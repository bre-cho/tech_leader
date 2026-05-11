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


class Customer(Base):
    __tablename__ = "customers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(64), nullable=True)
    metadata = Column(JSON, nullable=False, default=dict)
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
    asset_url = Column(Text, nullable=True)
    provider = Column(String(80), nullable=True)
    provider_job_id = Column(String(255), nullable=True)
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
    source_artifact_id = Column(String(255), nullable=True)
    score_snapshot = Column(JSON, nullable=False, default=dict)
    why_this_won = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UpsellOpportunity(Base):
    __tablename__ = "upsell_opportunities"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=False)
    image_variant_id = Column(UUID(as_uuid=True), nullable=True)
    upsell_video_potential_score = Column(Float, nullable=False, default=0)
    recommendation = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class VideoConcept(Base):
    __tablename__ = "video_concepts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=False)
    source_image_variant_id = Column(UUID(as_uuid=True), nullable=True)
    concept_payload = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class VideoStoryboard(Base):
    __tablename__ = "video_storyboards"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=False)
    render_job_id = Column(String(255), nullable=True)
    storyboard_payload = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class VideoOffer(Base):
    __tablename__ = "video_offers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=False)
    offer_payload = Column(JSON, nullable=False, default=dict)
    selected = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CRMFollowup(Base):
    __tablename__ = "crm_followups"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=False)
    sequence_payload = Column(JSON, nullable=False, default=dict)
    status = Column(String(64), nullable=False, default="scheduled")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PurchaseEvent(Base):
    __tablename__ = "purchase_events"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=False)
    event_type = Column(String(80), nullable=False)
    amount = Column(Float, nullable=True)
    payload = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class IndustryPlaybook(Base):
    __tablename__ = "industry_playbooks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    industry = Column(String(120), nullable=False, unique=True)
    playbook_payload = Column(JSON, nullable=False, default=dict)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class WorkflowEvent(Base):
    __tablename__ = "workflow_events"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=False)
    trace_id = Column(String(120), nullable=False, index=True)
    step = Column(String(120), nullable=False)
    payload = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ArtifactLineage(Base):
    __tablename__ = "artifact_lineage"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=False)
    trace_id = Column(String(120), nullable=False, index=True)
    step = Column(String(120), nullable=False)
    parent_step_id = Column(String(120), nullable=True)
    artifact_id = Column(String(120), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ReleaseGateReport(Base):
    __tablename__ = "release_gate_reports"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trace_id = Column(String(120), nullable=False, index=True)
    go_no_go = Column(String(16), nullable=False)
    report_payload = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MemoryUpdate(Base):
    __tablename__ = "memory_updates"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=False)
    trace_id = Column(String(120), nullable=False, index=True)
    memory_type = Column(String(64), nullable=False)
    payload = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
