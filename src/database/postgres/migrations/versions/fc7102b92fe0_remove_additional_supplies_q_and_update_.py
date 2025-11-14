"""Remove additional_supplies_q and update field requirements

Revision ID: fc7102b92fe0
Revises: ebbc0d93735a
Create Date: 2025-11-14 05:09:06.803415

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'fc7102b92fe0'
down_revision: Union[str, None] = 'ebbc0d93735a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("markets", "additional_supplies_q")


def downgrade() -> None:
    op.add_column(
        "markets",
        sa.Column("additional_supplies_q", sa.String(), nullable=True),
    )

