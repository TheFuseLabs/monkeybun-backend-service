"""remove_is_published_from_markets

Revision ID: 367a483a8c5c
Revises: a1b2c3d4e5f6
Create Date: 2025-11-30 20:28:44.239204

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '367a483a8c5c'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("markets", "is_published")


def downgrade() -> None:
    op.add_column(
        "markets",
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default="true"),
    )

