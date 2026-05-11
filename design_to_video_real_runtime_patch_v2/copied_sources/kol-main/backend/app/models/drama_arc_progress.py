"""Legacy compatibility shim for drama arc progress model.

This module keeps import compatibility for ``app.models.drama_arc_progress``
while avoiding duplicate SQLAlchemy table registration.
"""
from app.drama.models.arc_progress import DramaArcProgress

__all__ = ["DramaArcProgress"]
