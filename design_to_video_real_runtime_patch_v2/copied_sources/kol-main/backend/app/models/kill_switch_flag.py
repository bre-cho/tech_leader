from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class KillSwitchFlag(Base):
    """ORM model for the ``kill_switch_flags`` table.

    Table created by Alembic migration ``20260505_0034_kill_switch_flags``.

    Each row records the enabled/disabled state of one named feature flag.
    The table is used by :class:`~app.services.kill_switch.KillSwitch` as a
    durable fallback when Redis is unavailable so flag state survives worker
    restarts even during Redis outages.
    """

    __tablename__ = "kill_switch_flags"

    feature_name: Mapped[str] = mapped_column(
        String(255), primary_key=True, nullable=False
    )
    enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true", default=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )
