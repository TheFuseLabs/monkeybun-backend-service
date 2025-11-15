"""Add twitter and facebook to business

Revision ID: 63310c522125
Revises: fc7102b92fe0
Create Date: 2025-01-27 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "63310c522125"
down_revision: Union[str, None] = "fc7102b92fe0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "businesses",
        sa.Column("twitter_handle", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )
    op.add_column(
        "businesses",
        sa.Column("facebook_handle", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("businesses", "facebook_handle")
    op.drop_column("businesses", "twitter_handle")

