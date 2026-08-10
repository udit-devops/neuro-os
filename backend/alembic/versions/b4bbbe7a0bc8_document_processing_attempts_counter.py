"""document processing attempts counter

Revision ID: b4bbbe7a0bc8
Revises: c493281a0bd9
Create Date: 2026-08-10 15:32:40.241296

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b4bbbe7a0bc8'
down_revision: Union[str, Sequence[str], None] = 'c493281a0bd9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add the processing attempts counter used for bounded retries."""
    op.add_column(
        "documents",
        sa.Column("processing_attempts", sa.Integer(), server_default="0", nullable=False),
    )


def downgrade() -> None:
    """Remove the processing attempts counter."""
    op.drop_column("documents", "processing_attempts")
