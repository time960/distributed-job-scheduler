"""worker heartbeats

Revision ID: 004
Revises: 003
Create Date: 2026-05-11 12:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table('workers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('worker_id', sa.String(), nullable=False),
        sa.Column('hostname', sa.String(), nullable=False),
        sa.Column('status', sa.Enum('ACTIVE', 'DEAD', 'STOPPED', name='workerstatus'), nullable=False),
        sa.Column('last_heartbeat_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('stopped_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('jobs_processed', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workers_worker_id'), 'workers', ['worker_id'], unique=True)

def downgrade() -> None:
    op.drop_index(op.f('ix_workers_worker_id'), table_name='workers')
    op.drop_table('workers')
    workerstatus = postgresql.ENUM('ACTIVE', 'DEAD', 'STOPPED', name='workerstatus')
    workerstatus.drop(op.get_bind())
