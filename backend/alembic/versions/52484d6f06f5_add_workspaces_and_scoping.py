"""add_workspaces_and_scoping

Revision ID: 52484d6f06f5
Revises: dda0c6122a2b
Create Date: 2026-10-21 16:41:26.644965

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '52484d6f06f5'
down_revision: Union[str, None] = 'dda0c6122a2b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "workspaces",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("token_hash", sa.String(), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_workspaces_token_hash", "workspaces", ["token_hash"], unique=True)
    op.add_column("policy_rules", sa.Column("workspace_id", sa.String(), sa.ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=True))
    op.add_column("simulation_runs", sa.Column("workspace_id", sa.String(), sa.ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=True))
    op.create_index("ix_policy_rules_workspace_id", "policy_rules", ["workspace_id"])
    op.create_index("ix_simulation_runs_workspace_id", "simulation_runs", ["workspace_id"])


def downgrade() -> None:
    op.drop_index("ix_simulation_runs_workspace_id", table_name="simulation_runs")
    op.drop_column("simulation_runs", "workspace_id")
    op.drop_index("ix_policy_rules_workspace_id", table_name="policy_rules")
    op.drop_column("policy_rules", "workspace_id")
    op.drop_index("ix_workspaces_token_hash", table_name="workspaces")
    op.drop_table("workspaces")
