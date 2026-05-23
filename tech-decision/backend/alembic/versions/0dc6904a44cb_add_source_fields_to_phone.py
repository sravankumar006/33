"""add_source_fields_to_phone

Revision ID: 0dc6904a44cb
Revises: 83180cf78a1c
Create Date: 2026-05-22 19:22:49.372440

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0dc6904a44cb'
down_revision: Union[str, None] = '83180cf78a1c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('phones') as batch_op:
        batch_op.add_column(sa.Column('source', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('source_url', sa.Text(), nullable=True))
        batch_op.alter_column('launch_price', existing_type=sa.Integer(), nullable=True)
        batch_op.alter_column('current_avg_price', existing_type=sa.Integer(), nullable=True)


def downgrade() -> None:
    with op.batch_alter_table('phones') as batch_op:
        batch_op.alter_column('current_avg_price', existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column('launch_price', existing_type=sa.Integer(), nullable=False)
        batch_op.drop_column('source_url')
        batch_op.drop_column('source')
