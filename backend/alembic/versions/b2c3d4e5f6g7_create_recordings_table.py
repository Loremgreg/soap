"""create_recordings_table

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2026-01-28 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6g7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create recordings table with indexes."""
    op.create_table(
        'recordings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('duration_seconds', sa.Integer(), nullable=False),
        sa.Column('language_detected', sa.String(10), nullable=True),
        sa.Column('transcript_text', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='processing'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Create indexes
    op.create_index('idx_recordings_user_id', 'recordings', ['user_id'])
    op.create_index('idx_recordings_created_at', 'recordings', ['created_at'])
    op.create_index('idx_recordings_status', 'recordings', ['status'])
    op.create_index('idx_recordings_updated_at', 'recordings', ['updated_at'])


def downgrade() -> None:
    """Drop recordings table with indexes."""
    op.drop_index('idx_recordings_updated_at', table_name='recordings')
    op.drop_index('idx_recordings_status', table_name='recordings')
    op.drop_index('idx_recordings_created_at', table_name='recordings')
    op.drop_index('idx_recordings_user_id', table_name='recordings')
    op.drop_table('recordings')
