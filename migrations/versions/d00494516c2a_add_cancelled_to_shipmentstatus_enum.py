"""add cancelled to shipmentstatus enum

Revision ID: d00494516c2a
Revises: bf80f7482f34
Create Date: 2026-04-10 16:40:18.258057

"""
from typing import Sequence, Union

import sqlmodel
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd00494516c2a'
down_revision: Union[str, Sequence[str], None] = 'bf80f7482f34'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE shipmentstatus ADD VALUE 'cancelled'")


def downgrade() -> None:
    pass
