"""merge branches

Revision ID: 29324cab9635
Revises: a1b2c3d4e5f6, ee3c91007b14
Create Date: 2026-05-22 22:54:17.692089

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '29324cab9635'
down_revision: Union[str, None] = ('a1b2c3d4e5f6', 'ee3c91007b14')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
