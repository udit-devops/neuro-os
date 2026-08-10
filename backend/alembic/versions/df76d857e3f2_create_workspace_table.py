"""create workspace table

Revision ID: df76d857e3f2
Revises: 100bc9fee362
Create Date: 2026-07-31 23:39:47.908797

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'df76d857e3f2'
down_revision: Union[str, Sequence[str], None] = '100bc9fee362'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the workspace table."""
    op.create_table(
        "workspace",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_workspace_id", "workspace", ["id"])
    op.create_index("ix_workspace_name", "workspace", ["name"])


def downgrade() -> None:
    """Drop the workspace table."""
    op.drop_index("ix_workspace_name", table_name="workspace")
    op.drop_index("ix_workspace_id", table_name="workspace")
    op.drop_table("workspace")
