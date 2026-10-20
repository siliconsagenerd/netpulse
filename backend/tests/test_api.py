from fastapi.testclient import TestClient


def test_health(client: "TestClient"):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_rules_crud(client):
    r = client.post("/api/rules", json={"name": "t", "priority": 5, "action": "block", "match_client": "*", "match_domain": "*"})
    assert r.status_code == 200
    rid = r.json()["id"]
    r = client.get("/api/rules")
    assert any(x["id"] == rid for x in r.json())
    r = client.patch(f"/api/rules/{rid}/toggle")
    assert r.status_code == 200
    r = client.delete(f"/api/rules/{rid}")
    assert r.status_code == 200


def test_invalid_action_rejected(client):
    r = client.post("/api/rules", json={"name": "t", "priority": 5, "action": "nope"})
    assert r.status_code == 422


def test_simulate_and_report(client):
    r = client.post("/api/simulate", json={"seed": 1, "duration_seconds": 5, "request_rate": 5})
    assert r.status_code == 200
    run_id = r.json()["id"]
    assert r.json()["status"] == "completed"
    assert r.json()["summary"]["total_events"] > 0
    ev = client.get(f"/api/runs/{run_id}/events?limit=10")
    assert ev.status_code == 200
    assert len(ev.json()) > 0
    rep = client.get(f"/api/runs/{run_id}/report")
    assert rep.status_code == 200
    assert rep.json()["run_id"] == run_id
    assert "assertions" in rep.json()
    dash = client.get(f"/api/dashboard?run_id={run_id}")
    assert dash.status_code == 200
    assert dash.json()["summary"] is not None


def test_events_filter(client):
    r = client.post("/api/simulate", json={"seed": 2, "duration_seconds": 5, "request_rate": 4})
    run_id = r.json()["id"]
    ev = client.get(f"/api/runs/{run_id}/events?action=block")
    assert ev.status_code == 200
    for e in ev.json():
        assert e["action"] == "block"


def test_clients_domains(client):
    r = client.get("/api/clients")
    assert r.status_code == 200
    assert len(r.json()) >= 1
    r = client.get("/api/domains")
    assert r.status_code == 200
    assert len(r.json()) >= 1
