import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from ..core.database import Base


def gen_id():
    return str(uuid.uuid4())


class Client(Base):
    __tablename__ = "clients"
    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, nullable=False, unique=True)
    ip = Column(String, nullable=False)
    group = Column(String, default="default")
    created_at = Column(DateTime, default=datetime.utcnow)


class Domain(Base):
    __tablename__ = "domains"
    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, nullable=False, unique=True)
    category = Column(String, default="general")
    created_at = Column(DateTime, default=datetime.utcnow)


class Workspace(Base):
    __tablename__ = "workspaces"
    id = Column(String, primary_key=True, default=gen_id)
    token_hash = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_seen_at = Column(DateTime, default=datetime.utcnow)

class PolicyRule(Base):
    __tablename__ = "policy_rules"
    id = Column(String, primary_key=True, default=gen_id)
    workspace_id = Column(String, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=True)
    name = Column(String, nullable=False)
    priority = Column(Integer, default=100)
    enabled = Column(Boolean, default=True)
    match_client = Column(String, nullable=True)  # '*' matches any client
    match_domain = Column(String, nullable=True)  # 'category:x' or a domain
    action = Column(String, nullable=False)  # allow, block, rate_limit, route
    rate_limit_per_min = Column(Integer, nullable=True)
    route_to = Column(String, nullable=True)
    reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SimulationRun(Base):
    __tablename__ = "simulation_runs"
    id = Column(String, primary_key=True, default=gen_id)
    workspace_id = Column(String, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=True)
    seed = Column(Integer, nullable=False)
    duration_seconds = Column(Integer, default=60)
    request_rate = Column(Integer, default=10)  # requests per second
    cache_ttl = Column(Integer, default=30)
    cache_capacity = Column(Integer, default=100)
    cache_policy = Column(String, default="lru")
    status = Column(String, default="completed")
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    summary = Column(JSON, nullable=True)


class RequestEvent(Base):
    __tablename__ = "request_events"
    id = Column(String, primary_key=True, default=gen_id)
    run_id = Column(String, ForeignKey("simulation_runs.id", ondelete="CASCADE"), nullable=False)
    ts = Column(Float, nullable=False)  # seconds since run start
    client = Column(String, nullable=False)
    domain = Column(String, nullable=False)
    action = Column(String, nullable=False)  # allow, block, rate_limit, route
    reason = Column(String, nullable=True)
    matched_rule = Column(String, nullable=True)
    cache = Column(String, nullable=False)  # hit or miss
    status_code = Column(Integer, nullable=False)
    latency_ms = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class CacheEntry(Base):
    __tablename__ = "cache_entries"
    id = Column(String, primary_key=True, default=gen_id)
    run_id = Column(String, ForeignKey("simulation_runs.id", ondelete="CASCADE"), nullable=False)
    domain = Column(String, nullable=False)
    cached_at = Column(Float, nullable=False)
    expires_at = Column(Float, nullable=False)
    hits = Column(Integer, default=0)
