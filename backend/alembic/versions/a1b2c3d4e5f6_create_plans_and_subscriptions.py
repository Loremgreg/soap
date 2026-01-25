"""create_plans_and_subscriptions

Revision ID: a1b2c3d4e5f6
Revises: 8f19ab8e77cf
Create Date: 2026-01-25 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '8f19ab8e77cf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create plans and subscriptions tables with indexes and seed data."""
    # Create plans table
    op.create_table(
        'plans',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('display_name', sa.String(100), nullable=False),
        sa.Column('price_monthly', sa.Integer(), nullable=False),
        sa.Column('quota_monthly', sa.Integer(), nullable=False),
        sa.Column('max_recording_minutes', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('max_notes_retention', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )

    # Create indexes for plans
    op.create_index('idx_plans_name', 'plans', ['name'])
    op.create_index(
        'idx_plans_active',
        'plans',
        ['is_active'],
        postgresql_where=sa.text('is_active = true')
    )

    # Seed plans data
    op.execute("""
        INSERT INTO plans (name, display_name, price_monthly, quota_monthly, max_recording_minutes, max_notes_retention)
        VALUES
            ('starter', 'Starter', 2900, 20, 10, 10),
            ('pro', 'Pro', 4900, 50, 10, 10)
    """)

    # Create subscriptions table
    op.create_table(
        'subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('plan_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='trial'),
        sa.Column('quota_remaining', sa.Integer(), nullable=False),
        sa.Column('quota_total', sa.Integer(), nullable=False),
        sa.Column('trial_ends_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('current_period_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('current_period_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('stripe_customer_id', sa.String(255), nullable=True),
        sa.Column('stripe_subscription_id', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['plan_id'], ['plans.id']),
        sa.UniqueConstraint('user_id', name='unique_user_subscription'),
    )

    # Create indexes for subscriptions
    op.create_index('idx_subscriptions_user_id', 'subscriptions', ['user_id'])
    op.create_index('idx_subscriptions_status', 'subscriptions', ['status'])
    op.create_index(
        'idx_subscriptions_trial_ends_at',
        'subscriptions',
        ['trial_ends_at'],
        postgresql_where=sa.text("status = 'trial'")
    )


def downgrade() -> None:
    """Drop subscriptions and plans tables with indexes."""
    # Drop subscriptions indexes and table
    op.drop_index('idx_subscriptions_trial_ends_at', table_name='subscriptions')
    op.drop_index('idx_subscriptions_status', table_name='subscriptions')
    op.drop_index('idx_subscriptions_user_id', table_name='subscriptions')
    op.drop_table('subscriptions')

    # Drop plans indexes and table
    op.drop_index('idx_plans_active', table_name='plans')
    op.drop_index('idx_plans_name', table_name='plans')
    op.drop_table('plans')
