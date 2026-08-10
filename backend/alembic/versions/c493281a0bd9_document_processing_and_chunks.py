"""document processing and chunks

Revision ID: c493281a0bd9
Revises: d23d980cea38
Create Date: 2026-08-10 15:25:40.727004

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = 'c493281a0bd9'
down_revision: Union[str, Sequence[str], None] = 'd23d980cea38'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add document processing lifecycle and the vector-backed chunks table."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.add_column("documents", sa.Column("processing_status", sa.String(length=20), server_default="UPLOADED", nullable=False))
    op.add_column("documents", sa.Column("error_message", sa.Text(), nullable=True))
    op.add_column("documents", sa.Column("processing_started_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("documents", sa.Column("processing_completed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("documents", sa.Column("chunk_count", sa.Integer(), server_default="0", nullable=False))
    op.create_index("ix_documents_processing_status", "documents", ["processing_status"])

    op.create_table(
        "chunks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "document_id",
            sa.Integer(),
            sa.ForeignKey("documents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "workspace_id",
            sa.Integer(),
            sa.ForeignKey("workspace.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("embedding", Vector(768), nullable=True),
        sa.Column("char_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_chunks_id", "chunks", ["id"])
    op.create_index("ix_chunks_document_id", "chunks", ["document_id"])
    op.create_index("ix_chunks_workspace_id", "chunks", ["workspace_id"])
    op.create_index("ix_chunks_content_hash", "chunks", ["content_hash"])


def downgrade() -> None:
    """Drop chunks and the document processing columns."""
    op.drop_index("ix_chunks_content_hash", table_name="chunks")
    op.drop_index("ix_chunks_workspace_id", table_name="chunks")
    op.drop_index("ix_chunks_document_id", table_name="chunks")
    op.drop_index("ix_chunks_id", table_name="chunks")
    op.drop_table("chunks")

    op.drop_index("ix_documents_processing_status", table_name="documents")
    op.drop_column("documents", "chunk_count")
    op.drop_column("documents", "processing_completed_at")
    op.drop_column("documents", "processing_started_at")
    op.drop_column("documents", "error_message")
    op.drop_column("documents", "processing_status")
