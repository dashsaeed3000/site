from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from ..config.settings import settings

_engine = None
_SessionLocal = None
_ScopedSession = None


def engine_factory():
    """Create (or return) the global SQLAlchemy engine and base Session factory."""
    global _engine, _SessionLocal
    if _engine is None:
        # DB_URI will include dialect+driver
        _engine = create_engine(settings.DB_URI, pool_pre_ping=True)
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    return _engine


def get_session() -> Generator[Session, None, None]:
    """Yield a short-lived Session instance (for regular request/DB usage)."""
    global _SessionLocal
    if _SessionLocal is None:
        engine_factory()
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_scoped_session():
    """
    Return a scoped_session suitable for integrations that expect a
    long-lived Session/registry object (e.g., Flask-Admin).
    """
    global _ScopedSession, _SessionLocal
    if _ScopedSession is None:
        if _SessionLocal is None:
            engine_factory()
        _ScopedSession = scoped_session(_SessionLocal)
    return _ScopedSession
