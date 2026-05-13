"""cron scheduling

Revision ID: 003
Revises: 002
Create Date: 2026-05-11 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table('schedules',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('cron_expression', sa.String(), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.Column('max_attempts', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('last_run_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_run_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_schedules_name'), 'schedules', ['name'], unique=False)
    
    op.add_column('jobs', sa.Column('schedule_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(None, 'jobs', 'schedules', ['schedule_id'], ['id'])

def downgrade() -> None:
    op.drop_constraint(None, 'jobs', type_='foreignkey')
    op.drop_column('jobs', 'schedule_id')
    op.drop_index(op.f('ix_schedules_name'), table_name='schedules')
    op.drop_table('schedules')
