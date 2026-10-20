import pytest
from app.schemas import SimulationRequest
from app.simulation.engine import run_simulation
from app.core.database import SessionLocal


def test_simulation_deterministic():
    db = SessionLocal()
    try:
        req = SimulationRequest(seed=7, duration_seconds=5, request_rate=4, cache_ttl=10, cache_capacity=20, cache_policy="lru")
        r1 = run_simulation(db, req)
        r2 = run_simulation(db, req)
        assert r1.summary["total_events"] == r2.summary["total_events"]
        assert r1.summary["cache_hit_ratio"] == r2.summary["cache_hit_ratio"]
        assert r1.summary["blocked"] == r2.summary["blocked"]
    finally:
        db.close()


def test_simulation_bad_params_rejected_by_schema():
    with pytest.raises(Exception):
        SimulationRequest(seed=1, duration_seconds=0, request_rate=4, cache_ttl=10, cache_capacity=20, cache_policy="lru")
