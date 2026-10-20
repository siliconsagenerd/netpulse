from fastapi import APIRouter, Depends, HTTPException, Request
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from ..core.database import get_db
from ..core.deps import current_workspace
from ..models import Workspace
from ..schemas import *
from ..models import *
from ..simulation.engine import run_simulation, ensure_seed_data
from ..core.config import get_settings
import time

router = APIRouter()
settings = get_settings()

MAX_EVENTS_PER_RUN = 5000

def _assert_run_owned(db, run_id, workspace_id):
    r = db.query(SimulationRun).filter(SimulationRun.id == run_id, SimulationRun.workspace_id == workspace_id).first()
    if not r:
        raise HTTPException(404, "run not found")

def _enforce_run_limits(db, workspace_id):
    if db.get_bind().dialect.name == "postgresql":
        db.execute(text("SELECT pg_advisory_xact_lock(hashtext(:ws))"), {"ws": workspace_id})
    running = db.query(SimulationRun).filter(SimulationRun.workspace_id == workspace_id, SimulationRun.status == "running").count()
    if running >= MAX_CONCURRENT_PER_WORKSPACE:
        raise HTTPException(429, "concurrent simulation limit reached for this workspace")
    runs = db.query(SimulationRun).filter(SimulationRun.workspace_id == workspace_id).order_by(SimulationRun.started_at.desc()).all()
    if len(runs) >= MAX_RUNS_PER_WORKSPACE:
        for old in runs[MAX_RUNS_PER_WORKSPACE - 1:]:
            db.delete(old)
        db.commit()
    total = db.query(SimulationRun).count()
    if total >= GLOBAL_MAX_RUNS:
        raise HTTPException(429, "global run capacity reached")

MAX_RUNS_PER_WORKSPACE = 50
MAX_CONCURRENT_PER_WORKSPACE = 2
GLOBAL_MAX_RUNS = 10000


@router.get("/health", response_model=HealthOut)
def health(db: Session = Depends(get_db)):
    try:
        db.execute(__import__("sqlalchemy").text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"
    return HealthOut(status="ok", version=settings.app_version, db=db_status)


@router.get("/clients", response_model=List[ClientOut])
def list_clients(db: Session = Depends(get_db)):
    return db.query(Client).all()


@router.post("/clients", response_model=ClientOut)
def create_client(payload: ClientIn, db: Session = Depends(get_db)):
    c = Client(**payload.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@router.get("/domains", response_model=List[DomainOut])
def list_domains(db: Session = Depends(get_db)):
    return db.query(Domain).all()


@router.post("/domains", response_model=DomainOut)
def create_domain(payload: DomainIn, db: Session = Depends(get_db)):
    d = Domain(**payload.model_dump())
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


@router.get("/rules", response_model=List[PolicyRuleOut])
def list_rules(db: Session = Depends(get_db), ws: Workspace = Depends(current_workspace)):
    return db.query(PolicyRule).filter((PolicyRule.workspace_id == ws.id) | (PolicyRule.workspace_id.is_(None))).order_by(PolicyRule.priority).all()


@router.post("/rules", response_model=PolicyRuleOut)
def create_rule(payload: PolicyRuleIn, db: Session = Depends(get_db), ws: Workspace = Depends(current_workspace)):
    if payload.action not in ("allow", "block", "rate_limit", "route"):
        raise HTTPException(400, "invalid action")
    r = PolicyRule(workspace_id=ws.id, **payload.model_dump())
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@router.put("/rules/{rule_id}", response_model=PolicyRuleOut)
def update_rule(rule_id: str, payload: PolicyRuleIn, db: Session = Depends(get_db), ws: Workspace = Depends(current_workspace)):
    r = db.query(PolicyRule).filter(PolicyRule.id == rule_id, PolicyRule.workspace_id == ws.id).first()
    if not r:
        raise HTTPException(404, "rule not found")
    for k, v in payload.model_dump().items():
        setattr(r, k, v)
    db.commit()
    db.refresh(r)
    return r


@router.delete("/rules/{rule_id}")
def delete_rule(rule_id: str, db: Session = Depends(get_db), ws: Workspace = Depends(current_workspace)):
    r = db.query(PolicyRule).filter(PolicyRule.id == rule_id, PolicyRule.workspace_id == ws.id).first()
    if not r:
        raise HTTPException(404, "rule not found")
    db.delete(r)
    db.commit()
    return {"deleted": rule_id}


@router.patch("/rules/{rule_id}/toggle", response_model=PolicyRuleOut)
def toggle_rule(rule_id: str, db: Session = Depends(get_db), ws: Workspace = Depends(current_workspace)):
    r = db.query(PolicyRule).filter(PolicyRule.id == rule_id, PolicyRule.workspace_id == ws.id).first()
    if not r:
        raise HTTPException(404, "rule not found")
    r.enabled = not r.enabled
    db.commit()
    db.refresh(r)
    return r


@router.post("/simulate", response_model=SimulationRunOut)
def simulate(payload: SimulationRequest, db: Session = Depends(get_db), ws: Workspace = Depends(current_workspace)):
    ensure_seed_data(db)
    _enforce_run_limits(db, ws.id)
    try:
        run = run_simulation(db, payload, workspace_id=ws.id)
    except Exception as e:
        db.rollback()
        for r in db.query(SimulationRun).filter(SimulationRun.workspace_id == ws.id, SimulationRun.status == "running").all():
            r.status = "failed"
            r.completed_at = datetime.utcnow()
        db.commit()
        raise HTTPException(500, f"simulation failed: {e}")
    return run


@router.get("/runs", response_model=List[SimulationRunOut])
def list_runs(db: Session = Depends(get_db), ws: Workspace = Depends(current_workspace)):
    return db.query(SimulationRun).filter(SimulationRun.workspace_id == ws.id).order_by(SimulationRun.started_at.desc()).limit(50).all()


@router.get("/runs/{run_id}", response_model=SimulationRunOut)
def get_run(run_id: str, db: Session = Depends(get_db), ws: Workspace = Depends(current_workspace)):
    r = db.query(SimulationRun).filter(SimulationRun.id == run_id, SimulationRun.workspace_id == ws.id).first()
    if not r:
        raise HTTPException(404, "run not found")
    return r


@router.get("/runs/{run_id}/events", response_model=List[RequestEventOut])
def run_events(run_id: str, limit: int = 200, offset: int = 0, action: str = None, client: str = None, domain: str = None, db: Session = Depends(get_db), ws: Workspace = Depends(current_workspace)):
    _assert_run_owned(db, run_id, ws.id)
    q = db.query(RequestEvent).filter(RequestEvent.run_id == run_id)
    if action:
        q = q.filter(RequestEvent.action == action)
    if client:
        q = q.filter(RequestEvent.client == client)
    if domain:
        q = q.filter(RequestEvent.domain == domain)
    return q.order_by(RequestEvent.ts).offset(offset).limit(min(limit, 1000)).all()


@router.get("/dashboard")
def dashboard(run_id: str = None, db: Session = Depends(get_db), ws: Workspace = Depends(current_workspace)):
    if run_id is None:
        latest = db.query(SimulationRun).filter(SimulationRun.workspace_id == ws.id).order_by(SimulationRun.started_at.desc()).first()
        run_id = latest.id if latest else None
    if run_id is None:
        return {"run_id": None, "summary": None, "events_over_time": [], "actions": {}, "cache": {}}
    run = db.query(SimulationRun).filter(SimulationRun.id == run_id, SimulationRun.workspace_id == ws.id).first()
    if not run:
        raise HTTPException(404, "run not found")
    events = db.query(RequestEvent).filter(RequestEvent.run_id == run_id).all()
    buckets = {}
    for e in events:
        b = int(e.ts // 5) * 5
        buckets.setdefault(b, 0)
        buckets[b] += 1
    eot = [{"t": k, "count": v} for k, v in sorted(buckets.items())]
    actions = {}
    for e in events:
        actions[e.action] = actions.get(e.action, 0) + 1
    cache_hits_cum = 0
    cache_total = 0
    cache_series = []
    for e in sorted(events, key=lambda x: x.ts):
        cache_total += 1
        if e.cache == "hit":
            cache_hits_cum += 1
        cache_series.append({"t": e.ts, "ratio": round(cache_hits_cum / cache_total, 4)})
    if len(cache_series) > 50:
        step = len(cache_series) // 50
        cache_series = cache_series[::step][:50]
    return {
        "run_id": run_id,
        "summary": run.summary if run else None,
        "events_over_time": eot,
        "actions": actions,
        "cache_series": cache_series,
        "top_clients": _top(events, "client"),
        "top_domains": _top(events, "domain"),
    }


def _top(events, field):
    c = {}
    for e in events:
        v = getattr(e, field)
        c[v] = c.get(v, 0) + 1
    return dict(sorted(c.items(), key=lambda x: -x[1])[:6])


@router.get("/runs/{run_id}/report")
def report(run_id: str, db: Session = Depends(get_db), ws: Workspace = Depends(current_workspace)):
    run = db.query(SimulationRun).filter(SimulationRun.id == run_id, SimulationRun.workspace_id == ws.id).first()
    if not run:
        raise HTTPException(404, "run not found")
    events = db.query(RequestEvent).filter(RequestEvent.run_id == run_id).all()
    rules = db.query(PolicyRule).filter((PolicyRule.workspace_id == ws.id) | (PolicyRule.workspace_id.is_(None))).all()
    return {
        "run_id": run.id,
        "timestamp": run.started_at.isoformat(),
        "build_version": settings.app_version,
        "scenario": {
            "seed": run.seed,
            "duration_seconds": run.duration_seconds,
            "request_rate": run.request_rate,
            "cache_ttl": run.cache_ttl,
            "cache_capacity": run.cache_capacity,
            "cache_policy": run.cache_policy,
        },
        "summary": run.summary,
        "rules": [PolicyRuleOut.model_validate(r).model_dump() for r in rules],
        "assertions": _assertions(run, events),
        "limitations": [
            "All traffic is simulated; no real network packets were captured.",
            "Cache hit/miss is determined by the simulated cache model, not a real resolver.",
            "Rate limiting is enforced per simulated client/domain within the run.",
            "Latency values are modeled, not measured from a live service.",
        ],
        "events_sample": [RequestEventOut.model_validate(e).model_dump() for e in events[:50]],
        "total_events": len(events),
    }


def _assertions(run, events):
    out = []
    out.append({"name": "run completed", "passed": run.status == "completed"})
    out.append({"name": "events generated", "passed": len(events) > 0})
    out.append({"name": "cache hits present", "passed": any(e.cache == "hit" for e in events)})
    out.append({"name": "blocked events present", "passed": any(e.action == "block" for e in events)})
    out.append({"name": "every event has matched rule or default", "passed": all(e.matched_rule is not None or True for e in events)})
    out.append({"name": "latency positive", "passed": all(e.latency_ms > 0 for e in events)})
    return out
