"""create document table

Revision ID: d23d980cea38
Revises: 08d7f6f68912
Create Date: 2026-08-04 01:26:25.540850

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd23d980cea38'
down_revision: Union[str, Sequence[str], None] = '08d7f6f68912'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the documents table with per-workspace composite index."""
    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("file_type", sa.String(length=100), nullable=True),
        sa.Column(
            "workspace_id",
            sa.Integer(),
            sa.ForeignKey("workspace.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(
        "ix_documents_workspace_created_id",
        "documents",
        ["workspace_id", "created_at", "id"],
    )


def downgrade() -> None:
    """Drop the document table and its index."""
    op.drop_index("ix_documents_workspace_created_id", table_name="documents")
    op.drop_table("documents")
