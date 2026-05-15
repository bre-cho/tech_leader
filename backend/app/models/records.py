from sqlalchemy import Integer, String, Text, Float, DateTime, Boolean, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base

class WorkflowRunRecord(Base):
    __tablename__ = "workflow_runs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    workflow_id: Mapped[str] = mapped_column(String(80), index=True)
    workflow_name: Mapped[str] = mapped_column(String(120), index=True)
    status: Mapped[str] = mapped_column(String(40), default="running", index=True)
    input_json: Mapped[str] = mapped_column(Text)
    output_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    verification_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    promotion_status: Mapped[str | None] = mapped_column(String(80), nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

class WinnerDNARecord(Base):
    __tablename__ = "winner_dna"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    industry: Mapped[str] = mapped_column(String(120), index=True)
    visual_type: Mapped[str] = mapped_column(String(120))
    hook: Mapped[str] = mapped_column(Text)
    offer: Mapped[str] = mapped_column(Text)
    conversion_score: Mapped[float] = mapped_column(Float, default=0)
    upsell_rate: Mapped[float] = mapped_column(Float, default=0)
    storyboard_pattern: Mapped[str] = mapped_column(Text)
    payload_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now())

class ContextEntityRecord(Base):
    __tablename__ = "context_entities"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(120), index=True)
    entity_key: Mapped[str] = mapped_column(String(240), unique=True, index=True)
    payload_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

class ContextRelationRecord(Base):
    __tablename__ = "context_relations"
    __table_args__ = (
        UniqueConstraint("source_key", "relation_type", "target_key", name="uq_context_relations_triplet"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_key: Mapped[str] = mapped_column(String(240), index=True)
    relation_type: Mapped[str] = mapped_column(String(120), index=True)
    target_key: Mapped[str] = mapped_column(String(240), index=True)
    payload_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now())

class AgentTrustRecord(Base):
    __tablename__ = "agent_trust"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    agent_name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    trust_score: Mapped[float] = mapped_column(Float, default=0)
    sample_count: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[str] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

class ReplaySnapshotRecord(Base):
    __tablename__ = "replay_snapshots"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    snapshot_id: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    workflow_id: Mapped[str] = mapped_column(String(80), index=True)
    payload_json: Mapped[str] = mapped_column(Text)
    output_hash: Mapped[str] = mapped_column(String(128), index=True)
    input_hash: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    runtime_version: Mapped[str | None] = mapped_column(String(40), nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now())


class StatePropagationRecord(Base):
    __tablename__ = "state_propagation_log"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    workflow_id: Mapped[str] = mapped_column(String(80), index=True)
    source_agent: Mapped[str] = mapped_column(String(120), index=True)
    target_agent: Mapped[str] = mapped_column(String(120), index=True)
    state_key: Mapped[str] = mapped_column(String(240))
    value_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now())


class RetryStateRecord(Base):
    __tablename__ = "retry_state"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    idempotency_key: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    workflow_id: Mapped[str] = mapped_column(String(80), index=True)
    agent_name: Mapped[str] = mapped_column(String(120))
    attempt_count: Mapped[int] = mapped_column(Integer, default=1)
    last_status: Mapped[str] = mapped_column(String(40), default="pending")
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class DecisionLogRecord(Base):
    __tablename__ = "decision_log"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    decision_id: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    workflow_id: Mapped[str] = mapped_column(String(80), index=True)
    decision_type: Mapped[str] = mapped_column(String(120), index=True)
    outcome: Mapped[str] = mapped_column(String(40), index=True)
    reason: Mapped[str] = mapped_column(Text)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now())
