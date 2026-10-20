import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import get_settings

_raw = os.environ.get("DATABASE_URL") or get_settings().database_url
DATABASE_URL = _raw.replace("postgresql://", "postgresql+psycopg2://", 1) if _raw.startswith("postgresql://") else _raw

_is_sqlite = DATABASE_URL.startswith("sqlite")
_connect_args = {"check_same_thread": False} if _is_sqlite else {}
_engine_kwargs = {"connect_args": _connect_args}
if not _is_sqlite:
    _engine_kwargs.update(pool_pre_ping=True, pool_recycle=300)
engine = create_engine(DATABASE_URL, **_engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
