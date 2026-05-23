"""phase4_spec_completion_offer_intelligence

Revision ID: a1b2c3d4e5f6
Revises: 5f892f5e313a
Create Date: 2026-05-22 21:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '5f892f5e313a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── phone_specs new columns ──────────────────────────────────────────────
    with op.batch_alter_table('phone_specs', schema=None) as batch_op:
        # Battery
        batch_op.add_column(sa.Column('reverse_charging', sa.Boolean(), nullable=True))

        # Display enrichments
        batch_op.add_column(sa.Column('hdr_support', sa.String(120), nullable=True))
        batch_op.add_column(sa.Column('display_protection', sa.String(120), nullable=True))
        batch_op.add_column(sa.Column('pwm_dimming', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('real_world_brightness_nits', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('brightness_label', sa.String(180), nullable=True))

        # Build
        batch_op.add_column(sa.Column('cooling_system', sa.String(180), nullable=True))
        batch_op.add_column(sa.Column('build_materials', sa.String(250), nullable=True))

        # Connectivity
        batch_op.add_column(sa.Column('wifi_version', sa.String(60), nullable=True))
        batch_op.add_column(sa.Column('bluetooth_version', sa.String(60), nullable=True))
        batch_op.add_column(sa.Column('usb_type', sa.String(80), nullable=True))
        batch_op.add_column(sa.Column('nfc', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('esim', sa.Boolean(), nullable=True))

        # Software
        batch_op.add_column(sa.Column('android_version', sa.String(60), nullable=True))
        batch_op.add_column(sa.Column('update_policy_label', sa.String(250), nullable=True))

        # Storage
        batch_op.add_column(sa.Column('ufs_type', sa.String(40), nullable=True))

        # AI
        batch_op.add_column(sa.Column('ai_features', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('ai_suite_name', sa.String(120), nullable=True))

        # Raw fields
        batch_op.add_column(sa.Column('raw_connectivity', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('raw_software', sa.Text(), nullable=True))

    # ── price_listings new columns ───────────────────────────────────────────
    with op.batch_alter_table('price_listings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('original_mrp', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('cashback_amount', sa.Integer(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('emi_available', sa.Boolean(), nullable=False, server_default=sa.false()))
        batch_op.add_column(sa.Column('emi_months', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('fake_discount_flag', sa.Boolean(), nullable=False, server_default=sa.false()))
        batch_op.add_column(sa.Column('discount_authenticity_score', sa.Integer(), nullable=False, server_default='100'))
        batch_op.add_column(sa.Column('price_intelligence_note', sa.Text(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('price_listings', schema=None) as batch_op:
        batch_op.drop_column('price_intelligence_note')
        batch_op.drop_column('discount_authenticity_score')
        batch_op.drop_column('fake_discount_flag')
        batch_op.drop_column('emi_months')
        batch_op.drop_column('emi_available')
        batch_op.drop_column('cashback_amount')
        batch_op.drop_column('original_mrp')

    with op.batch_alter_table('phone_specs', schema=None) as batch_op:
        batch_op.drop_column('raw_software')
        batch_op.drop_column('raw_connectivity')
        batch_op.drop_column('ai_suite_name')
        batch_op.drop_column('ai_features')
        batch_op.drop_column('ufs_type')
        batch_op.drop_column('update_policy_label')
        batch_op.drop_column('android_version')
        batch_op.drop_column('esim')
        batch_op.drop_column('nfc')
        batch_op.drop_column('usb_type')
        batch_op.drop_column('bluetooth_version')
        batch_op.drop_column('wifi_version')
        batch_op.drop_column('build_materials')
        batch_op.drop_column('cooling_system')
        batch_op.drop_column('brightness_label')
        batch_op.drop_column('real_world_brightness_nits')
        batch_op.drop_column('pwm_dimming')
        batch_op.drop_column('display_protection')
        batch_op.drop_column('hdr_support')
        batch_op.drop_column('reverse_charging')
