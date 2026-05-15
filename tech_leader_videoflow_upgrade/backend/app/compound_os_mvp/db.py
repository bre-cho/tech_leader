from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./creative_business_os.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class Brand(Base):
    __tablename__ = "brands"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)
    industry = Column(String)
    identity_json = Column(Text, default="{}")
    memory_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)

class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(Integer, primary_key=True)
    brand_id = Column(Integer, ForeignKey("brands.id"))
    name = Column(String)
    product_name = Column(String)
    product_type = Column(String)
    audience = Column(String)
    goal = Column(String)
    channel = Column(String)
    status = Column(String, default="draft")
    winning_variant_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    brand = relationship("Brand")

class CreativeVariant(Base):
    __tablename__ = "creative_variants"
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    name = Column(String)
    layout = Column(String)
    hook = Column(String)
    typography = Column(String)
    visual_style = Column(String)
    offer = Column(String)
    prompt = Column(Text)
    storyboard_json = Column(Text, default="[]")
    score = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    campaign = relationship("Campaign")

class MetricEvent(Base):
    __tablename__ = "metric_events"
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    variant_id = Column(Integer, ForeignKey("creative_variants.id"))
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    revenue = Column(Float, default=0)
    watch_time_rate = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class GraphEdge(Base):
    __tablename__ = "graph_edges"
    id = Column(Integer, primary_key=True)
    source = Column(String, index=True)
    relation = Column(String, index=True)
    target = Column(String, index=True)
    weight = Column(Float, default=0.5)
    evidence = Column(Text, default="")
    observations = Column(Integer, default=1)
    updated_at = Column(DateTime, default=datetime.utcnow)

class WinnerDNA(Base):
    __tablename__ = "winner_dna"
    id = Column(Integer, primary_key=True)
    brand_id = Column(Integer, ForeignKey("brands.id"))
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    variant_id = Column(Integer, ForeignKey("creative_variants.id"))
    dna_json = Column(Text)
    score = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class WorkflowRun(Base):
    __tablename__ = "workflow_runs"
    id = Column(Integer, primary_key=True)
    run_id = Column(String, unique=True, index=True)
    campaign_id = Column(Integer, nullable=True)
    stages_json = Column(Text)
    status = Column(String)
    report_json = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
