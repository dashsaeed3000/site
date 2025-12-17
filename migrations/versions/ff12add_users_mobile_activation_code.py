"""add users mobile and activation_code columns

Revision ID: ff12addusersmobilecode
Revises: e6f7g8h9i0j1
Create Date: 2025-12-18 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ff12addusersmobilecode'
down_revision: Union[str, Sequence[str], None] = 'e6f7g8h9i0j1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add nullable columns so existing deployments won't break.
    op.add_column('users', sa.Column('mobile', sa.String(length=30), nullable=True))
    op.add_column('users', sa.Column('activation_code', sa.String(length=32), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'activation_code')
    op.drop_column('users', 'mobile')
