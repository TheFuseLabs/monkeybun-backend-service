"""Update application status enum and remove internal tags

Revision ID: 5433ec7496cd
Revises: 63310c522125
Create Date: 2025-01-27 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5433ec7496cd"
down_revision: Union[str, None] = "63310c522125"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE applicationstatus AS ENUM ('applied', 'accepted', 'declined', 'confirmed')"
    )

    op.execute("""
        ALTER TABLE applications 
        ALTER COLUMN status TYPE applicationstatus 
        USING status::applicationstatus
    """)

    op.drop_column("applications", "internal_tags")


def downgrade() -> None:
    op.add_column(
        "applications",
        sa.Column("internal_tags", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )

    op.execute("ALTER TABLE applications ALTER COLUMN status TYPE VARCHAR(50)")

    op.execute("DROP TYPE applicationstatus")
