from sqlalchemy import Integer, String, Text, Float, DateTime, func
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
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_key: Mapped[str] = mapped_column(String(240), index=True)
    relation_type: Mapped[str] = mapped_column(String(120), index=True)
    target_key: Mapped[str] = mapped_column(String(240), index=True)
    payload_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now())
