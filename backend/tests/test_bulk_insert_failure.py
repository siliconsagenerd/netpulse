import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.core import database


def test_bulk_insert_failure_recovers(monkeypatch):
    """A failure during bulk insert must not leave a completed run or partial rows."""
    calls = {"n": 0}
    orig = Session.bulk_insert_mappings

    def failing(self, mapper, mappings, *a, **k):
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("injected bulk-insert failure")
        return orig(self, mapper, mappings, *a, **k)

    monkeypatch.setattr(Session, "bulk_insert_mappings", failing)

    c = TestClient(app)
    c.get("/api/rules")
    c.post("/api/rules", json={"name": "allow all", "priority": 1000, "enabled": True,
                               "match_client": "*", "match_domain": "*", "action": "allow"})

    r = c.post("/api/simulate", json={"seed": 1, "duration_seconds": 5,
                                     "request_rate": 2, "cache_ttl": 60,
                                     "cache_capacity": 10, "cache_policy": "lru"})
    assert r.status_code == 500, r.text

    runs = c.get("/api/runs").json()
    assert runs, "no run recorded"
    run = runs[0]
    assert run["status"] != "completed", run

    db = database.SessionLocal()
    try:
        from app.models import RequestEvent, CacheEntry, SimulationRun
        ev_count = db.query(RequestEvent).filter(RequestEvent.run_id == run["id"]).count()
        cache_count = db.query(CacheEntry).filter(CacheEntry.run_id == run["id"]).count()
        assert ev_count == 0, ev_count
        assert cache_count == 0, cache_count
        db_run = db.query(SimulationRun).filter(SimulationRun.id == run["id"]).first()
        assert db_run is not None
        assert db_run.status == "failed", db_run.status
    finally:
        db.close()

    monkeypatch.setattr(Session, "bulk_insert_mappings", orig)
    r2 = c.post("/api/simulate", json={"seed": 2, "duration_seconds": 5,
                                      "request_rate": 2, "cache_ttl": 60,
                                      "cache_capacity": 10, "cache_policy": "lru"})
    assert r2.status_code == 200, r2.text
    assert r2.json()["status"] == "completed"
