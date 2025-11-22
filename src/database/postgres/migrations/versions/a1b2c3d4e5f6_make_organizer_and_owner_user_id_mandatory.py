"""make_organizer_and_owner_user_id_mandatory

Revision ID: a1b2c3d4e5f6
Revises: 9f075399cc41
Create Date: 2025-11-22 14:15:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "9f075399cc41"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "DELETE FROM markets WHERE organizer_user_id IS NULL"
    )
    op.execute(
        "DELETE FROM businesses WHERE owner_user_id IS NULL"
    )
    op.alter_column("markets", "organizer_user_id", nullable=False)
    op.alter_column("businesses", "owner_user_id", nullable=False)


def downgrade() -> None:
    op.alter_column("markets", "organizer_user_id", nullable=True)
    op.alter_column("businesses", "owner_user_id", nullable=True)

