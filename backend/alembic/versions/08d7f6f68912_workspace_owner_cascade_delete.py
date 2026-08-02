"""workspace owner cascade delete

Revision ID: 08d7f6f68912
Revises: df76d857e3f2
Create Date: 2026-08-02 14:00:32.446776

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '08d7f6f68912'
down_revision: Union[str, Sequence[str], None] = 'df76d857e3f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Alter workspace.owner_id FK to ON DELETE CASCADE."""
    op.drop_constraint("workspace_owner_id_fkey", "workspace", type_="foreignkey")
    op.create_foreign_key(
        "workspace_owner_id_fkey",
        "workspace",
        "users",
        ["owner_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Restore FK without ON DELETE CASCADE."""
    op.drop_constraint("workspace_owner_id_fkey", "workspace", type_="foreignkey")
    op.create_foreign_key(
        "workspace_owner_id_fkey",
        "workspace",
        "users",
        ["owner_id"],
        ["id"],
    )
