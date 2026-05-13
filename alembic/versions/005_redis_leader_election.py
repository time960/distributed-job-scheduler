"""redis leader election

Revision ID: 005
Revises: 004
Create Date: 2026-05-11 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('jobs', sa.Column('scheduled_for', sa.DateTime(timezone=True), nullable=True))
    op.create_unique_constraint('uq_job_schedule_time', 'jobs', ['schedule_id', 'scheduled_for'])


def downgrade() -> None:
    op.drop_constraint('uq_job_schedule_time', 'jobs', type_='unique')
    op.drop_column('jobs', 'scheduled_for')
