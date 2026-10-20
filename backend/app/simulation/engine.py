import random
from datetime import datetime
from collections import OrderedDict, defaultdict
from sqlalchemy.orm import Session
from ..models import Client, Domain, PolicyRule, SimulationRun, RequestEvent, CacheEntry, Workspace, gen_id


def default_clients():
    return [
        ("client-a", "10.0.0.11", "lan"),
        ("client-b", "10.0.0.12", "lan"),
        ("client-c", "10.0.0.21", "guest"),
        ("client-d", "10.0.0.31", "dmz"),
    ]


def default_domains():
    return [
        ("example.com", "general"),
        ("api.example.com", "api"),
        ("cdn.example.com", "cdn"),
        ("ads.tracker.net", "ads"),
        ("malware.example.org", "malware"),
        ("updates.example.com", "updates"),
    ]


def ensure_seed_data(db: Session):
    changed = False
    if db.query(Client).count() == 0:
        for name, ip, grp in default_clients():
            db.add(Client(name=name, ip=ip, group=grp))
        changed = True
    if db.query(Domain).count() == 0:
        for name, cat in default_domains():
            db.add(Domain(name=name, category=cat))
        changed = True
    if changed:
        db.commit()

def seed_default_rules(db: Session, workspace_id: str):
    if db.query(PolicyRule).filter(PolicyRule.workspace_id == workspace_id).count() > 0:
        return
    seeds = [
        ("Block malware domains", 10, True, "*", "category:malware", "block", None, None, "Malware category blocked"),
        ("Block ads", 20, True, "*", "category:ads", "block", None, None, "Ad/tracker blocked"),
        ("Rate limit guest API", 30, True, "group:guest", "category:api", "rate_limit", 5, None, "Guest API rate limited"),
        ("Route updates via alt resolver", 40, True, "*", "updates.example.com", "route", None, "resolver-b", "Routed to alternate resolver"),
        ("Allow all", 1000, True, "*", "*", "allow", None, None, "Default allow"),
    ]
    for name, prio, en, mc, md, action, rlim, route, reason in seeds:
        db.add(PolicyRule(workspace_id=workspace_id, name=name, priority=prio, enabled=en, match_client=mc,
                          match_domain=md, action=action, rate_limit_per_min=rlim,
                          route_to=route, reason=reason))
    db.commit()


def match_rule(rules, client_name, client_group, domain, category):
    # lowest priority number wins; disabled rules skipped
    candidates = []
    for r in rules:
        if not r.enabled:
            continue
        if not client_matches(r.match_client, client_name, client_group):
            continue
        if not domain_matches(r.match_domain, domain, category):
            continue
        candidates.append(r)
    if not candidates:
        return None
    candidates.sort(key=lambda r: (r.priority, r.name))
    return candidates[0]


def client_matches(pattern, client_name, client_group):
    if pattern in (None, "", "*"):
        return True
    if pattern.startswith("group:"):
        return client_group == pattern.split(":", 1)[1]
    return pattern == client_name


def domain_matches(pattern, domain, category):
    if pattern in (None, "", "*"):
        return True
    if pattern.startswith("category:"):
        return category == pattern.split(":", 1)[1]
    return pattern == domain


def recover_stale_runs(db: Session, stale_minutes: int = 10):
    from datetime import datetime, timedelta
    cutoff = datetime.utcnow() - timedelta(minutes=stale_minutes)
    stale = db.query(SimulationRun).filter(
        SimulationRun.status == "running",
        SimulationRun.started_at < cutoff,
    ).all()
    for r in stale:
        r.status = "interrupted"
        r.completed_at = datetime.utcnow()
    db.commit()
    return len(stale)

def run_simulation(db: Session, req, workspace_id: str = None) -> SimulationRun:
    ensure_seed_data(db)
    rng = random.Random(req.seed)
    run = SimulationRun(
        workspace_id=workspace_id,
        seed=req.seed,
        duration_seconds=req.duration_seconds,
        request_rate=req.request_rate,
        cache_ttl=req.cache_ttl,
        cache_capacity=req.cache_capacity,
        cache_policy=req.cache_policy,
        status="running",
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    clients = db.query(Client).all()
    domains = db.query(Domain).all()
    rules = db.query(PolicyRule).filter((PolicyRule.workspace_id == workspace_id) | (PolicyRule.workspace_id.is_(None))).all()

    if req.clients:
        clients = [c for c in clients if c.name in req.clients]
    if req.domains:
        domains = [d for d in domains if d.name in req.domains]
    if not clients or not domains:
        run.status = "failed"
        db.commit()
        return run

    group_of = {c.name: c.group for c in clients}

    cache = OrderedDict()
    rate_hits = defaultdict(list)

    total = req.duration_seconds * req.request_rate
    if total > 5000:
        total = 5000

    t = 0.0
    step = 1.0 / req.request_rate
    events = []
    for i in range(total):
        t = i * step
        if t > req.duration_seconds:
            break
        client = rng.choice(clients)
        domain = rng.choice(domains)
        client_name = client.name
        client_group = group_of[client_name]
        domain_name = domain.name
        category = domain.category

        rl_window = [x for x in rate_hits[(client_name, domain_name)] if t - x < 60.0]
        rate_hits[(client_name, domain_name)] = rl_window

        rule = match_rule(rules, client_name, client_group, domain_name, category)
        action = rule.action if rule else "allow"
        matched = rule.name if rule else None
        reason = rule.reason if rule else "No matching rule"

        if action == "rate_limit":
            rlim = rule.rate_limit_per_min or 5
            if len(rl_window) >= rlim:
                action = "block"
                reason = "Rate limit exceeded"
            else:
                rate_hits[(client_name, domain_name)].append(t)

        cache_status = "miss"
        if action in ("allow", "route"):
            entry = cache.get(domain_name)
            if entry is not None and entry["expires"] > t:
                cache_status = "hit"
                entry["hits"] += 1
                cache.move_to_end(domain_name)
            else:
                if len(cache) >= req.cache_capacity:
                    cache.popitem(last=False)
                cache[domain_name] = {"expires": t + req.cache_ttl, "hits": 0}
        # blocks are not cached

        base = 12.0 if cache_status == "hit" else 45.0
        latency = max(1.0, rng.gauss(base, base * 0.25))
        if action == "block":
            latency = max(1.0, rng.gauss(8.0, 2.0))
        if action == "route":
            latency = latency * 1.3

        status_code = 200
        if action == "block":
            status_code = 403
        elif action == "rate_limit":
            status_code = 429

        ev = {
            "id": gen_id(),
            "run_id": run.id,
            "ts": round(t, 3),
            "client": client_name,
            "domain": domain_name,
            "action": action,
            "reason": reason,
            "matched_rule": matched,
            "cache": cache_status,
            "status_code": status_code,
            "latency_ms": round(latency, 2),
        }
        events.append(ev)

    db.bulk_insert_mappings(RequestEvent, events)
    db.commit()

    cache_rows = [
        {"id": gen_id(), "run_id": run.id, "domain": domain_name,
         "cached_at": entry["expires"] - req.cache_ttl,
         "expires_at": entry["expires"], "hits": entry["hits"]}
        for domain_name, entry in cache.items()
    ]
    if cache_rows:
        db.bulk_insert_mappings(CacheEntry, cache_rows)
    db.commit()

    total_events = len(events)
    hits = sum(1 for e in events if e["cache"] == "hit")
    blocks = sum(1 for e in events if e["action"] == "block")
    rate_limited = sum(1 for e in events if e["action"] == "rate_limit")
    routed = sum(1 for e in events if e["action"] == "route")
    allowed = sum(1 for e in events if e["action"] == "allow")
    avg_latency = round(sum(e["latency_ms"] for e in events) / total_events, 2) if total_events else 0.0
    top_domains = {}
    for e in events:
        top_domains[e["domain"]] = top_domains.get(e["domain"], 0) + 1
    top_domains = dict(sorted(top_domains.items(), key=lambda x: -x[1])[:5])

    run.summary = {
        "total_events": total_events,
        "cache_hits": hits,
        "cache_misses": total_events - hits,
        "cache_hit_ratio": round(hits / total_events, 4) if total_events else 0.0,
        "allowed": allowed,
        "blocked": blocks,
        "rate_limited": rate_limited,
        "routed": routed,
        "avg_latency_ms": avg_latency,
        "top_domains": top_domains,
        "cache_final_size": len(cache),
    }
    run.status = "completed"
    run.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(run)
    return run
