from __future__ import annotations

from sqlalchemy import Column, String, Boolean, DateTime, JSON
from app.db.base import Base


class ReleaseGateState(Base):
    __tablename__ = "release_gate_states"

    id = Column(String(255), primary_key=True)
    gate_name = Column(String(255))
    is_open = Column(Boolean, default=False)
    feature_flags = Column(JSON)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
