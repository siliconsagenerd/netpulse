from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from typing import Optional, List
from datetime import datetime


class ClientIn(BaseModel):
    name: str
    ip: str
    group: str = "default"


class ClientOut(ClientIn):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime


class DomainIn(BaseModel):
    name: str
    category: str = "general"


class DomainOut(DomainIn):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime


class PolicyRuleIn(BaseModel):
    name: str
    priority: int = 100
    enabled: bool = True
    match_client: Optional[str] = "*"
    match_domain: Optional[str] = "*"
    action: str
    rate_limit_per_min: Optional[int] = None
    route_to: Optional[str] = None
    reason: Optional[str] = None

    @field_validator("action")
    @classmethod
    def _action(cls, v):
        if v not in ("allow", "block", "rate_limit", "route"):
            raise ValueError("invalid action")
        return v

    @model_validator(mode="after")
    def _params(self):
        if self.action == "rate_limit":
            if not self.rate_limit_per_min or self.rate_limit_per_min < 1:
                raise ValueError("rate_limit_per_min must be a positive integer for rate_limit rules")
        if self.action == "route":
            if not self.route_to or not self.route_to.strip():
                raise ValueError("route_to must be a non-empty resolver target for route rules")
        return self


class PolicyRuleOut(PolicyRuleIn):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime
    updated_at: datetime


class SimulationRequest(BaseModel):
    seed: int = 42
    duration_seconds: int = Field(60, ge=5, le=300)
    request_rate: int = Field(10, ge=1, le=50)
    cache_ttl: int = Field(30, ge=1, le=600)
    cache_capacity: int = Field(100, ge=10, le=1000)
    cache_policy: str = "lru"

    @field_validator("cache_policy")
    @classmethod
    def _cache_policy(cls, v):
        if v not in ("lru",):
            raise ValueError("unsupported cache policy; only 'lru' is supported")
        return v
    clients: Optional[List[str]] = None
    domains: Optional[List[str]] = None


class SimulationRunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    seed: int
    duration_seconds: int
    request_rate: int
    cache_ttl: int
    cache_capacity: int
    cache_policy: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    summary: Optional[dict] = None


class RequestEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    run_id: str
    ts: float
    client: str
    domain: str
    action: str
    reason: Optional[str] = None
    matched_rule: Optional[str] = None
    cache: str
    status_code: int
    latency_ms: float


class HealthOut(BaseModel):
    status: str
    version: str
    db: str
