"""Add unique constraint to applications

Revision ID: b9a05cf5a38a
Revises: 52bd2a8c1586
Create Date: 2025-01-27 15:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b9a05cf5a38a"
down_revision: Union[str, None] = "52bd2a8c1586"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "applications_market_id_business_id_key",
        "applications",
        ["market_id", "business_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "applications_market_id_business_id_key",
        "applications",
        type_="unique",
    )
