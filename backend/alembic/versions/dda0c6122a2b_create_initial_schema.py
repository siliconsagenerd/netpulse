"""create_initial_schema

Revision ID: dda0c6122a2b
Revises: 158419935847
Create Date: 2026-10-21 16:32:18.444281

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'dda0c6122a2b'
down_revision: Union[str, None] = '158419935847'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "clients",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False, unique=True),
        sa.Column("ip", sa.String(), nullable=False),
        sa.Column("group", sa.String(), nullable=True, server_default="default"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_clients_name", "clients", ["name"], unique=True)

    op.create_table(
        "domains",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False, unique=True),
        sa.Column("category", sa.String(), nullable=True, server_default="general"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_domains_name", "domains", ["name"], unique=True)

    op.create_table(
        "policy_rules",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=True, server_default="100"),
        sa.Column("enabled", sa.Boolean(), nullable=True, server_default="1"),
        sa.Column("match_client", sa.String(), nullable=True),
        sa.Column("match_domain", sa.String(), nullable=True),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("rate_limit_per_min", sa.Integer(), nullable=True),
        sa.Column("route_to", sa.String(), nullable=True),
        sa.Column("reason", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "simulation_runs",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("seed", sa.Integer(), nullable=False),
        sa.Column("duration_seconds", sa.Integer(), nullable=True, server_default="60"),
        sa.Column("request_rate", sa.Integer(), nullable=True, server_default="10"),
        sa.Column("cache_ttl", sa.Integer(), nullable=True, server_default="30"),
        sa.Column("cache_capacity", sa.Integer(), nullable=True, server_default="100"),
        sa.Column("cache_policy", sa.String(), nullable=True, server_default="lru"),
        sa.Column("status", sa.String(), nullable=True, server_default="completed"),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("summary", sa.JSON(), nullable=True),
    )

    op.create_table(
        "request_events",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("run_id", sa.String(), sa.ForeignKey("simulation_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("ts", sa.Float(), nullable=False),
        sa.Column("client", sa.String(), nullable=False),
        sa.Column("domain", sa.String(), nullable=False),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("reason", sa.String(), nullable=True),
        sa.Column("matched_rule", sa.String(), nullable=True),
        sa.Column("cache", sa.String(), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=False),
        sa.Column("latency_ms", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_request_events_run_id", "request_events", ["run_id"])

    op.create_table(
        "cache_entries",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("run_id", sa.String(), sa.ForeignKey("simulation_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("domain", sa.String(), nullable=False),
        sa.Column("cached_at", sa.Float(), nullable=False),
        sa.Column("expires_at", sa.Float(), nullable=False),
        sa.Column("hits", sa.Integer(), nullable=True, server_default="0"),
    )
    op.create_index("ix_cache_entries_run_id", "cache_entries", ["run_id"])


def downgrade() -> None:
    op.drop_index("ix_cache_entries_run_id", table_name="cache_entries")
    op.drop_table("cache_entries")
    op.drop_index("ix_request_events_run_id", table_name="request_events")
    op.drop_table("request_events")
    op.drop_table("simulation_runs")
    op.drop_table("policy_rules")
    op.drop_index("ix_domains_name", table_name="domains")
    op.drop_table("domains")
    op.drop_index("ix_clients_name", table_name="clients")
    op.drop_table("clients")
