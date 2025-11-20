"""add_cost_fields_to_markets

Revision ID: 605dba9c6c57
Revises: 56130e4a802e
Create Date: 2025-11-20 16:53:20.788108

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '605dba9c6c57'
down_revision: Union[str, None] = '56130e4a802e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('markets', sa.Column('is_free', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('markets', sa.Column('cost_amount', sa.Float(), nullable=True))
    op.add_column('markets', sa.Column('cost_currency', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('markets', 'cost_currency')
    op.drop_column('markets', 'cost_amount')
    op.drop_column('markets', 'is_free')

