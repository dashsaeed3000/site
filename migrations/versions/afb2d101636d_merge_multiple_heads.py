"""merge multiple heads

Revision ID: afb2d101636d
Revises: cb24bf16b8d3, ff12addusersmobilecode
Create Date: 2025-12-18 01:12:04.842489

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'afb2d101636d'
down_revision: Union[str, Sequence[str], None] = ('cb24bf16b8d3', 'ff12addusersmobilecode')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

