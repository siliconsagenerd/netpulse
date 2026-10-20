CREATE TABLE IF NOT EXISTS clients (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    ip VARCHAR(45) NOT NULL UNIQUE,
    "group" VARCHAR(60) NOT NULL DEFAULT 'default',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_clients_group ON clients("group");

CREATE TABLE IF NOT EXISTS domains (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(253) NOT NULL UNIQUE,
    category VARCHAR(60) NOT NULL DEFAULT 'general',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_domains_category ON domains(category);

CREATE TABLE IF NOT EXISTS policy_rules (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    priority INTEGER NOT NULL DEFAULT 100,
    enabled BOOLEAN NOT NULL DEFAULT true,
    match_client VARCHAR(120) NOT NULL DEFAULT '*',
    match_domain VARCHAR(253) NOT NULL DEFAULT '*',
    action VARCHAR(20) NOT NULL DEFAULT 'allow',
    params JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ck_rule_priority CHECK (priority >= 0 AND priority <= 10000),
    CONSTRAINT ck_rule_action CHECK (action IN ('allow','block','rate_limit','route'))
);
CREATE INDEX IF NOT EXISTS ix_policy_rules_enabled ON policy_rules(enabled);
CREATE INDEX IF NOT EXISTS ix_policy_rules_priority ON policy_rules(priority);
CREATE INDEX IF NOT EXISTS ix_policy_rules_enabled_priority ON policy_rules(enabled, priority);

CREATE TABLE IF NOT EXISTS simulation_runs (
    id VARCHAR(36) PRIMARY KEY,
    seed INTEGER NOT NULL,
    duration_seconds INTEGER NOT NULL,
    request_rate INTEGER NOT NULL,
    cache_ttl INTEGER NOT NULL,
    cache_capacity INTEGER NOT NULL,
    cache_policy VARCHAR(10) NOT NULL DEFAULT 'lru',
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ,
    summary JSONB,
    CONSTRAINT ck_run_duration CHECK (duration_seconds > 0),
    CONSTRAINT ck_run_rate CHECK (request_rate > 0),
    CONSTRAINT ck_run_ttl CHECK (cache_ttl >= 0),
    CONSTRAINT ck_run_cap CHECK (cache_capacity > 0)
);
CREATE INDEX IF NOT EXISTS ix_simulation_runs_status ON simulation_runs(status);

CREATE TABLE IF NOT EXISTS request_events (
    id VARCHAR(36) PRIMARY KEY,
    run_id VARCHAR(36) NOT NULL REFERENCES simulation_runs(id) ON DELETE CASCADE,
    ts DOUBLE PRECISION NOT NULL,
    client VARCHAR(120) NOT NULL,
    domain VARCHAR(253) NOT NULL,
    action VARCHAR(20) NOT NULL,
    cache VARCHAR(10) NOT NULL,
    latency_ms DOUBLE PRECISION NOT NULL,
    detail JSONB
);
CREATE INDEX IF NOT EXISTS ix_request_events_run_id ON request_events(run_id);
CREATE INDEX IF NOT EXISTS ix_request_events_client ON request_events(client);
CREATE INDEX IF NOT EXISTS ix_request_events_domain ON request_events(domain);
CREATE INDEX IF NOT EXISTS ix_request_events_action ON request_events(action);
CREATE INDEX IF NOT EXISTS ix_request_events_run_ts ON request_events(run_id, ts);
CREATE INDEX IF NOT EXISTS ix_request_events_run_action ON request_events(run_id, action);

CREATE TABLE IF NOT EXISTS cache_entries (
    id VARCHAR(36) PRIMARY KEY,
    run_id VARCHAR(36) NOT NULL REFERENCES simulation_runs(id) ON DELETE CASCADE,
    domain VARCHAR(253) NOT NULL,
    cached_at DOUBLE PRECISION NOT NULL,
    expires_at DOUBLE PRECISION NOT NULL,
    hits INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS ix_cache_entries_run_id ON cache_entries(run_id);
CREATE INDEX IF NOT EXISTS ix_cache_entries_run_domain ON cache_entries(run_id, domain);
