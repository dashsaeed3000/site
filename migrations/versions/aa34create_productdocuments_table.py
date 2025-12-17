"""create ProductDocuments table

Revision ID: aa34createproductdocuments
Revises: ff12addusersmobilecode
Create Date: 2025-12-18 00:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aa34createproductdocuments'
down_revision: Union[str, Sequence[str], None] = 'ff12addusersmobilecode'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'ProductDocuments',
        sa.Column('Id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('ProductId', sa.String(length=36), nullable=False),
        sa.Column('FileUrl', sa.String(length=1000), nullable=False),
        sa.Column('FileName', sa.String(length=500), nullable=True),
        sa.Column('ContentType', sa.String(length=255), nullable=True),
        sa.Column('FileSize', sa.Integer(), nullable=True),
        sa.Column('SortOrder', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('IsDeleted', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('CreatedAt', sa.DateTime(), nullable=False),
        sa.Column('CreatedBy', sa.String(length=36), nullable=True),
        sa.Column('UpdatedAt', sa.DateTime(), nullable=True),
        sa.Column('UpdatedBy', sa.String(length=36), nullable=True),
        sa.Column('DeletedAt', sa.DateTime(), nullable=True),
        sa.Column('DeletedBy', sa.String(length=36), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('ProductDocuments')
