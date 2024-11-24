"""add timestamp to tasks

Revision ID: dbd7a6e1463c
Revises: 97ccdfa65b54
Create Date: 2024-11-20 10:57:47.299486

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dbd7a6e1463c'
down_revision: Union[str, None] = '97ccdfa65b54'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('task', sa.Column('timestamp', sa.BigInteger(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('task', 'timestamp')
    # ### end Alembic commands ###
