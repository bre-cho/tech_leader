from __future__ import annotations

import threading
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

_engine_lock = threading.Lock()
_engine: Engine | None = None
_session_factory: sessionmaker | None = None


def _get_engine() -> Engine:
    """Return the shared SQLAlchemy engine, creating it on first call.

    Deferring engine creation to first use prevents an import-time crash when
    ``DATABASE_URL`` is misconfigured, so unrelated application routes
    (health checks, status endpoints) remain available even if the DB is
    temporarily unreachable at startup.
    """
    global _engine
    if _engine is None:
        with _engine_lock:
            if _engine is None:
                _engine = create_engine(
                    settings.database_url,
                    pool_pre_ping=True,
                    future=True,
                )
    return _engine


def _get_session_factory() -> sessionmaker:
    """Return the shared session factory, creating it on first call."""
    global _session_factory
    if _session_factory is None:
        with _engine_lock:
            if _session_factory is None:
                _session_factory = sessionmaker(
                    bind=_get_engine(),
                    autoflush=False,
                    autocommit=False,
                    expire_on_commit=False,
                    class_=Session,
                )
    return _session_factory


class _LazySessionLocal:
    """Drop-in for a ``sessionmaker`` instance that defers engine creation.

    Supports ``SessionLocal()`` (returns a :class:`~sqlalchemy.orm.Session`).
    The returned ``Session`` is itself a context manager, so
    ``with SessionLocal() as db: ...`` works as expected — the context
    manager protocol is on the ``Session``, not on this factory object.
    """

    def __call__(self) -> Session:
        return _get_session_factory()()


SessionLocal = _LazySessionLocal()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()