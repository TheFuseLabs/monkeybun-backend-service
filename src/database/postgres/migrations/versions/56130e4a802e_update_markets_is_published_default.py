"""update_markets_is_published_default

Revision ID: 56130e4a802e
Revises: 40cd7ce5586b
Create Date: 2025-11-16 19:15:33.908484

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '56130e4a802e'
down_revision: Union[str, None] = '40cd7ce5586b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE markets SET is_published = TRUE WHERE is_published = FALSE")
    op.alter_column('markets', 'is_published',
                    existing_type=sa.Boolean(),
                    server_default='true',
                    nullable=False)


def downgrade() -> None:
    op.alter_column('markets', 'is_published',
                    existing_type=sa.Boolean(),
                    server_default='false',
                    nullable=False)

