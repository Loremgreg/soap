"""create_soap_notes_table

Revision ID: c3d4e5f6g7h8
Revises: b2c3d4e5f6g7
Create Date: 2026-02-07 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6g7h8'
down_revision: Union[str, Sequence[str], None] = 'b2c3d4e5f6g7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create soap_notes table with indexes."""
    op.create_table(
        'soap_notes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('recording_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('subjective', sa.Text(), nullable=False),
        sa.Column('objective', sa.Text(), nullable=False),
        sa.Column('assessment', sa.Text(), nullable=False),
        sa.Column('plan', sa.Text(), nullable=False),
        sa.Column('language', sa.String(5), nullable=False, server_default='fr'),
        sa.Column('format', sa.String(20), nullable=False, server_default='paragraph'),
        sa.Column('verbosity', sa.String(20), nullable=False, server_default='medium'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['recording_id'], ['recordings.id'], ondelete='CASCADE'),
    )

    # Create indexes
    op.create_index('idx_soap_notes_user_id', 'soap_notes', ['user_id'])
    op.create_index('idx_soap_notes_recording_id', 'soap_notes', ['recording_id'])


def downgrade() -> None:
    """Drop soap_notes table with indexes."""
    op.drop_index('idx_soap_notes_recording_id', table_name='soap_notes')
    op.drop_index('idx_soap_notes_user_id', table_name='soap_notes')
    op.drop_table('soap_notes')
