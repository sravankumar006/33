"""extend_phone_specs

Revision ID: 5f892f5e313a
Revises: 0dc6904a44cb
Create Date: 2026-05-22 20:14:58.209417

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5f892f5e313a'
down_revision: Union[str, None] = '0dc6904a44cb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use batch_alter_table for SQLite compatibility
    with op.batch_alter_table('phone_specs') as batch_op:
        # Add new columns
        batch_op.add_column(sa.Column('chipset', sa.String(length=180), nullable=True))
        batch_op.add_column(sa.Column('cpu', sa.String(length=250), nullable=True))
        batch_op.add_column(sa.Column('gpu', sa.String(length=180), nullable=True))
        batch_op.add_column(sa.Column('ram', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('storage', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('wireless_charging', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('display_resolution', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('refresh_rate', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('main_camera', sa.String(length=250), nullable=True))
        batch_op.add_column(sa.Column('ultrawide_camera', sa.String(length=250), nullable=True))
        batch_op.add_column(sa.Column('telephoto_camera', sa.String(length=250), nullable=True))
        batch_op.add_column(sa.Column('selfie_camera', sa.String(length=250), nullable=True))
        batch_op.add_column(sa.Column('weight', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('ip_rating', sa.String(length=80), nullable=True))
        
        # Add raw columns
        batch_op.add_column(sa.Column('raw_chipset', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('raw_cpu', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('raw_gpu', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('raw_ram', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('raw_storage', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('raw_battery_mah', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('raw_charging_watts', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('raw_wireless_charging', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('raw_display_size', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('raw_display_resolution', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('raw_refresh_rate', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('raw_display_type', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('raw_main_camera', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('raw_ultrawide_camera', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('raw_telephoto_camera', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('raw_selfie_camera', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('raw_weight', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('raw_ip_rating', sa.Text(), nullable=True))

        # Make existing columns nullable
        batch_op.alter_column('battery_mah', existing_type=sa.Integer(), nullable=True)
        batch_op.alter_column('charging_watts', existing_type=sa.Integer(), nullable=True)
        batch_op.alter_column('processor', existing_type=sa.String(length=180), nullable=True)
        batch_op.alter_column('ram_gb', existing_type=sa.Integer(), nullable=True)
        batch_op.alter_column('storage_gb', existing_type=sa.Integer(), nullable=True)
        batch_op.alter_column('display_size', existing_type=sa.Float(), nullable=True)
        batch_op.alter_column('display_type', existing_type=sa.String(length=120), nullable=True)
        batch_op.alter_column('refresh_rate_hz', existing_type=sa.Integer(), nullable=True)
        batch_op.alter_column('peak_brightness_nits', existing_type=sa.Integer(), nullable=True)
        batch_op.alter_column('camera_main_mp', existing_type=sa.Integer(), nullable=True)
        batch_op.alter_column('os_updates_years', existing_type=sa.Integer(), nullable=True)
        batch_op.alter_column('security_updates_years', existing_type=sa.Integer(), nullable=True)


def downgrade() -> None:
    with op.batch_alter_table('phone_specs') as batch_op:
        batch_op.alter_column('battery_mah', existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column('charging_watts', existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column('processor', existing_type=sa.String(length=180), nullable=False)
        batch_op.alter_column('ram_gb', existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column('storage_gb', existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column('display_size', existing_type=sa.Float(), nullable=False)
        batch_op.alter_column('display_type', existing_type=sa.String(length=120), nullable=False)
        batch_op.alter_column('refresh_rate_hz', existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column('peak_brightness_nits', existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column('camera_main_mp', existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column('os_updates_years', existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column('security_updates_years', existing_type=sa.Integer(), nullable=False)

        batch_op.drop_column('chipset')
        batch_op.drop_column('cpu')
        batch_op.drop_column('gpu')
        batch_op.drop_column('ram')
        batch_op.drop_column('storage')
        batch_op.drop_column('wireless_charging')
        batch_op.drop_column('display_resolution')
        batch_op.drop_column('refresh_rate')
        batch_op.drop_column('main_camera')
        batch_op.drop_column('ultrawide_camera')
        batch_op.drop_column('telephoto_camera')
        batch_op.drop_column('selfie_camera')
        batch_op.drop_column('weight')
        batch_op.drop_column('ip_rating')
        batch_op.drop_column('raw_chipset')
        batch_op.drop_column('raw_cpu')
        batch_op.drop_column('raw_gpu')
        batch_op.drop_column('raw_ram')
        batch_op.drop_column('raw_storage')
        batch_op.drop_column('raw_battery_mah')
        batch_op.drop_column('raw_charging_watts')
        batch_op.drop_column('raw_wireless_charging')
        batch_op.drop_column('raw_display_size')
        batch_op.drop_column('raw_display_resolution')
        batch_op.drop_column('raw_refresh_rate')
        batch_op.drop_column('raw_display_type')
        batch_op.drop_column('raw_main_camera')
        batch_op.drop_column('raw_ultrawide_camera')
        batch_op.drop_column('raw_telephoto_camera')
        batch_op.drop_column('raw_selfie_camera')
        batch_op.drop_column('raw_weight')
        batch_op.drop_column('raw_ip_rating')
