"""Add payment enums to applications

Revision ID: 52bd2a8c1586
Revises: 78e6a52997c7
Create Date: 2025-01-27 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "52bd2a8c1586"
down_revision: Union[str, None] = "78e6a52997c7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TYPE paymentmethod AS ENUM (
            'bank_transfer', 'credit_card', 'paypal', 'check', 'cash', 'other'
        )
    """)
    
    op.execute("""
        CREATE TYPE paymentstatus AS ENUM (
            'pending', 'paid', 'failed', 'refunded'
        )
    """)
    
    op.execute("""
        ALTER TABLE applications 
        ALTER COLUMN payment_method TYPE paymentmethod 
        USING CASE 
            WHEN payment_method IS NULL THEN NULL
            ELSE payment_method::paymentmethod
        END
    """)
    
    op.execute("""
        ALTER TABLE applications 
        ALTER COLUMN payment_status TYPE paymentstatus 
        USING CASE 
            WHEN payment_status IS NULL THEN NULL
            ELSE payment_status::paymentstatus
        END
    """)


def downgrade() -> None:
    op.execute("ALTER TABLE applications ALTER COLUMN payment_method TYPE VARCHAR(50)")
    op.execute("ALTER TABLE applications ALTER COLUMN payment_status TYPE VARCHAR(50)")
    op.execute("DROP TYPE paymentstatus")
    op.execute("DROP TYPE paymentmethod")

