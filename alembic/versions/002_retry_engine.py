"""retry engine

Revision ID: 002
Revises: 001
Create Date: 2026-05-11 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('jobs', sa.Column('error_message', sa.String(), nullable=True))
    op.add_column('jobs', sa.Column('next_retry_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('jobs', sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True))

def downgrade() -> None:
    op.drop_column('jobs', 'completed_at')
    op.drop_column('jobs', 'next_retry_at')
    op.drop_column('jobs', 'error_message')
