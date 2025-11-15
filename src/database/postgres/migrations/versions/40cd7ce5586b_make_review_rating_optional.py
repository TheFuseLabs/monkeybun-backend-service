"""Make review rating optional

Revision ID: 40cd7ce5586b
Revises: b9a05cf5a38a
Create Date: 2025-01-27 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "40cd7ce5586b"
down_revision: Union[str, None] = "b9a05cf5a38a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("reviews_rating_check", "reviews", type_="check")
    op.alter_column("reviews", "rating", nullable=True)
    op.create_check_constraint(
        "reviews_rating_check",
        "reviews",
        "rating IS NULL OR (rating >= 1 AND rating <= 5)",
    )


def downgrade() -> None:
    op.drop_constraint("reviews_rating_check", "reviews", type_="check")
    op.alter_column("reviews", "rating", nullable=False)
    op.create_check_constraint(
        "reviews_rating_check",
        "reviews",
        "rating >= 1 AND rating <= 5",
    )
