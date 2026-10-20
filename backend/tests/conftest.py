import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# fall back to a throwaway sqlite file when DATABASE_URL is unset
if not os.environ.get("DATABASE_URL"):
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.environ["DATABASE_URL"] = f"sqlite:///{path}"

from app.core.config import get_settings
get_settings.cache_clear()
from app.core.database import Base, engine, SessionLocal
from app.main import app

Base.metadata.create_all(bind=engine)
from app.simulation.engine import ensure_seed_data
s = SessionLocal()
try:
    ensure_seed_data(s)
finally:
    s.close()

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def db():
    s = SessionLocal()
    try:
        yield s
    finally:
        s.close()
