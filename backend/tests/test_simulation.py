from app.simulation.engine import match_rule, client_matches, domain_matches
from app.models import PolicyRule


def mk(name, prio, enabled, mc, md, action):
    r = PolicyRule(name=name, priority=prio, enabled=enabled, match_client=mc, match_domain=md, action=action)
    return r


def test_client_matches():
    assert client_matches("*", "a", "lan") is True
    assert client_matches("a", "a", "lan") is True
    assert client_matches("b", "a", "lan") is False
    assert client_matches("group:lan", "a", "lan") is True
    assert client_matches("group:guest", "a", "lan") is False


def test_domain_matches():
    assert domain_matches("*", "x.com", "general") is True
    assert domain_matches("x.com", "x.com", "general") is True
    assert domain_matches("category:ads", "x.com", "ads") is True
    assert domain_matches("category:ads", "x.com", "general") is False


def test_match_rule_precedence():
    rules = [
        mk("allow all", 1000, True, "*", "*", "allow"),
        mk("block malware", 10, True, "*", "category:malware", "block"),
    ]
    r = match_rule(rules, "c", "lan", "evil.org", "malware")
    assert r.name == "block malware"
    assert r.action == "block"


def test_disabled_rule_skipped():
    rules = [mk("block", 10, False, "*", "*", "block")]
    r = match_rule(rules, "c", "lan", "x.com", "general")
    assert r is None


def test_simulation_deterministic():
    from app.schemas import SimulationRequest
    from app.core.database import SessionLocal
    from app.simulation.engine import run_simulation, ensure_seed_data
    db = SessionLocal()
    ensure_seed_data(db)
    req = SimulationRequest(seed=7, duration_seconds=5, request_rate=4)
    r1 = run_simulation(db, req)
    req2 = SimulationRequest(seed=7, duration_seconds=5, request_rate=4)
    r2 = run_simulation(db, req2)
    assert r1.summary["total_events"] == r2.summary["total_events"]
    assert r1.summary["cache_hit_ratio"] == r2.summary["cache_hit_ratio"]
    db.close()
