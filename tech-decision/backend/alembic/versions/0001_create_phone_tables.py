"""create phone tables

Revision ID: 0001_create_phone_tables
Revises: 
Create Date: 2026-05-21 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg


revision = '0001_create_phone_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'phones',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('brand', sa.String(length=120), nullable=False),
        sa.Column('model', sa.String(length=180), nullable=False),
        sa.Column('slug', sa.String(length=210), nullable=False, unique=True),
        sa.Column('launch_price', sa.Integer(), nullable=False),
        sa.Column('current_avg_price', sa.Integer(), nullable=False),
        sa.Column('image_url', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    op.create_index('ix_phones_brand', 'phones', ['brand'])
    op.create_index('ix_phones_model', 'phones', ['model'])
    op.create_index('ix_phones_slug', 'phones', ['slug'], unique=True)
    op.create_index('ix_phones_created_at', 'phones', ['created_at'])

    op.create_table(
        'phone_specs',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('phone_id', pg.UUID(as_uuid=True), sa.ForeignKey('phones.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('battery_mah', sa.Integer(), nullable=False),
        sa.Column('charging_watts', sa.Integer(), nullable=False),
        sa.Column('processor', sa.String(length=180), nullable=False),
        sa.Column('ram_gb', sa.Integer(), nullable=False),
        sa.Column('storage_gb', sa.Integer(), nullable=False),
        sa.Column('display_size', sa.Float(), nullable=False),
        sa.Column('display_type', sa.String(length=120), nullable=False),
        sa.Column('refresh_rate_hz', sa.Integer(), nullable=False),
        sa.Column('peak_brightness_nits', sa.Integer(), nullable=False),
        sa.Column('camera_main_mp', sa.Integer(), nullable=False),
        sa.Column('os_updates_years', sa.Integer(), nullable=False),
        sa.Column('security_updates_years', sa.Integer(), nullable=False),
    )
    op.create_index('ix_phone_specs_phone_id', 'phone_specs', ['phone_id'])

    op.create_table(
        'phone_insights',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('phone_id', pg.UUID(as_uuid=True), sa.ForeignKey('phones.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('battery_summary', sa.Text(), nullable=False),
        sa.Column('performance_summary', sa.Text(), nullable=False),
        sa.Column('display_summary', sa.Text(), nullable=False),
        sa.Column('camera_summary', sa.Text(), nullable=False),
        sa.Column('software_summary', sa.Text(), nullable=False),
        sa.Column('honest_verdict', sa.Text(), nullable=False),
    )
    op.create_index('ix_phone_insights_phone_id', 'phone_insights', ['phone_id'])


def downgrade() -> None:
    op.drop_index('ix_phone_insights_phone_id', table_name='phone_insights')
    op.drop_table('phone_insights')
    op.drop_index('ix_phone_specs_phone_id', table_name='phone_specs')
    op.drop_table('phone_specs')
    op.drop_index('ix_phones_created_at', table_name='phones')
    op.drop_index('ix_phones_slug', table_name='phones')
    op.drop_index('ix_phones_model', table_name='phones')
    op.drop_index('ix_phones_brand', table_name='phones')
    op.drop_table('phones')
