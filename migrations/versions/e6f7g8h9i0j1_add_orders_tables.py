"""add orders tables

Revision ID: e6f7g8h9i0j1
Revises: a1b2c3d4e5f6
Create Date: 2024-01-01 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'e6f7g8h9i0j1'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create Orders table
    op.create_table(
        'Orders',
        sa.Column('Id', sa.String(length=36), nullable=False),
        sa.Column('UserId', sa.Integer(), nullable=True),
        sa.Column('OrderNumber', sa.String(length=50), nullable=False),
        sa.Column('Status', sa.String(length=20), nullable=False),
        sa.Column('PaymentStatus', sa.String(length=20), nullable=False),
        sa.Column('PaymentMethod', sa.String(length=50), nullable=True),
        sa.Column('PaymentTransactionId', sa.String(length=255), nullable=True),
        sa.Column('CustomerName', sa.String(length=255), nullable=False),
        sa.Column('CustomerPhone', sa.String(length=80), nullable=False),
        sa.Column('CustomerEmail', sa.String(length=120), nullable=True),
        sa.Column('ShippingAddress', sa.Text(), nullable=True),
        sa.Column('SubTotal', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('TaxAmount', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('ShippingCost', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('TotalAmount', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('Notes', sa.Text(), nullable=True),
        sa.Column('IsDeleted', sa.Boolean(), nullable=False),
        sa.Column('CreatedAt', sa.DateTime(), nullable=False),
        sa.Column('CreatedBy', sa.String(length=36), nullable=True),
        sa.Column('UpdatedAt', sa.DateTime(), nullable=True),
        sa.Column('UpdatedBy', sa.String(length=36), nullable=True),
        sa.Column('DeletedAt', sa.DateTime(), nullable=True),
        sa.Column('DeletedBy', sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(['UserId'], ['users.id'], ),
        sa.PrimaryKeyConstraint('Id'),
        sa.UniqueConstraint('OrderNumber')
    )
    op.create_index('ix_Orders_UserId', 'Orders', ['UserId'], unique=False)
    op.create_index('ix_Orders_CustomerPhone', 'Orders', ['CustomerPhone'], unique=False)
    op.create_index('ix_Orders_OrderNumber', 'Orders', ['OrderNumber'], unique=True)
    
    # Create OrderItems table
    op.create_table(
        'OrderItems',
        sa.Column('Id', sa.String(length=36), nullable=False),
        sa.Column('OrderId', sa.String(length=36), nullable=False),
        sa.Column('ProductId', sa.String(length=36), nullable=False),
        sa.Column('ProductTitle', sa.String(length=255), nullable=False),
        sa.Column('ProductSKU', sa.String(length=100), nullable=True),
        sa.Column('ProductPrice', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('Quantity', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('UnitPrice', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('TotalPrice', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('IsDeleted', sa.Boolean(), nullable=False),
        sa.Column('CreatedAt', sa.DateTime(), nullable=False),
        sa.Column('CreatedBy', sa.String(length=36), nullable=True),
        sa.Column('UpdatedAt', sa.DateTime(), nullable=True),
        sa.Column('UpdatedBy', sa.String(length=36), nullable=True),
        sa.Column('DeletedAt', sa.DateTime(), nullable=True),
        sa.Column('DeletedBy', sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(['OrderId'], ['Orders.Id'], ),
        sa.ForeignKeyConstraint(['ProductId'], ['Products.Id'], ),
        sa.PrimaryKeyConstraint('Id')
    )
    op.create_index('ix_OrderItems_OrderId', 'OrderItems', ['OrderId'], unique=False)
    op.create_index('ix_OrderItems_ProductId', 'OrderItems', ['ProductId'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_OrderItems_ProductId', table_name='OrderItems')
    op.drop_index('ix_OrderItems_OrderId', table_name='OrderItems')
    op.drop_table('OrderItems')
    op.drop_index('ix_Orders_OrderNumber', table_name='Orders')
    op.drop_index('ix_Orders_CustomerPhone', table_name='Orders')
    op.drop_index('ix_Orders_UserId', table_name='Orders')
    op.drop_table('Orders')

