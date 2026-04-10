"""add shipment event table

Revision ID: bf80f7482f34
Revises: a4fd14b6909e
Create Date: 2026-04-10 13:47:42.892674

"""
from typing import Sequence, Union

import sqlmodel
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'bf80f7482f34'
down_revision: Union[str, Sequence[str], None] = 'a4fd14b6909e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if 'shipment_event' not in tables:
        op.create_table(
            'shipment_event',
            sa.Column('id', sa.UUID(), nullable=False),
            sa.Column('created_at', postgresql.TIMESTAMP(), nullable=True),
            sa.Column('location', sa.Integer(), nullable=False),
            sa.Column('status', postgresql.ENUM(name='shipmentstatus', create_type=False), nullable=False),
            sa.Column('desription', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column('shipment_id', sa.Uuid(), nullable=False),
            sa.ForeignKeyConstraint(['shipment_id'], ['shipment.id'], ),
            sa.PrimaryKeyConstraint('id'),
        )

    seller_cols = [c['name'] for c in inspector.get_columns('seller')]
    if 'address' not in seller_cols:
        op.add_column('seller', sa.Column('address', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    if 'zip_code' not in seller_cols:
        op.add_column('seller', sa.Column('zip_code', sa.Integer(), nullable=True))

    shipment_cols = [c['name'] for c in inspector.get_columns('shipment')]
    if 'status' in shipment_cols:
        op.drop_column('shipment', 'status')
    if 'address' in shipment_cols:
        op.drop_column('shipment', 'address')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('shipment', sa.Column('address', sa.Integer(), nullable=True))
    op.add_column('shipment', sa.Column('status', sa.Enum('placed', 'in_transit', 'out_for_delivery', 'delivered', name='shipmentstatus', create_type=False), nullable=True))
    op.drop_column('seller', 'zip_code')
    op.drop_column('seller', 'address')
    op.drop_table('shipment_event')
