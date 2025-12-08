"""add site content table

Revision ID: a1b2c3d4e5f6
Revises: d5be0f3a7f92
Create Date: 2025-01-15 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'd5be0f3a7f92'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('SiteContent',
    sa.Column('Id', sa.String(length=36), nullable=False),
    sa.Column('SectionKey', sa.String(length=100), nullable=False),
    sa.Column('SectionName', sa.String(length=255), nullable=False),
    sa.Column('Title', sa.String(length=500), nullable=True),
    sa.Column('Subtitle', sa.String(length=500), nullable=True),
    sa.Column('Content', sa.Text(), nullable=True),
    sa.Column('ContentEn', sa.Text(), nullable=True),
    sa.Column('ContentAr', sa.Text(), nullable=True),
    sa.Column('ImageUrl', sa.String(length=500), nullable=True),
    sa.Column('VideoUrl', sa.String(length=500), nullable=True),
    sa.Column('LinkUrl', sa.String(length=500), nullable=True),
    sa.Column('LinkText', sa.String(length=255), nullable=True),
    sa.Column('Field1', sa.String(length=500), nullable=True),
    sa.Column('Field2', sa.String(length=500), nullable=True),
    sa.Column('Field3', sa.String(length=500), nullable=True),
    sa.Column('Field4', sa.String(length=500), nullable=True),
    sa.Column('JsonData', sa.Text(), nullable=True),
    sa.Column('SortOrder', sa.Integer(), nullable=False),
    sa.Column('IsActive', sa.Boolean(), nullable=False),
    sa.Column('IsDeleted', sa.Boolean(), nullable=False),
    sa.Column('CreatedAt', sa.DateTime(), nullable=False),
    sa.Column('CreatedBy', sa.String(length=36), nullable=True),
    sa.Column('UpdatedAt', sa.DateTime(), nullable=True),
    sa.Column('UpdatedBy', sa.String(length=36), nullable=True),
    sa.Column('DeletedAt', sa.DateTime(), nullable=True),
    sa.Column('DeletedBy', sa.String(length=36), nullable=True),
    sa.PrimaryKeyConstraint('Id'),
    sa.UniqueConstraint('SectionKey')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('SiteContent')
