"""added project ID and project name to logs

Revision ID: db871ba69fc4
Revises: 
Create Date: 2024-12-18 16:12:37.457199

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'db871ba69fc4'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('project',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=50), nullable=True),
    sa.Column('send_email', sa.Boolean(), nullable=True),
    sa.Column('archived', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('email', sa.String(length=50), nullable=True),
    sa.Column('password', sa.String(length=150), nullable=True),
    sa.Column('full_name', sa.String(length=50), nullable=True),
    sa.Column('permissions', sa.BigInteger(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('project_developers',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('user_id', sa.String(length=26), nullable=False),
    sa.Column('project_id', sa.String(length=26), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'project_id', name='uix_user_project')
    )
    op.create_table('remote_days',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('user_id', sa.String(length=26), nullable=False),
    sa.Column('day', sa.Date(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('task',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('project_id', sa.String(length=26), nullable=False),
    sa.Column('project_name', sa.String(length=100), nullable=False),
    sa.Column('user_id', sa.String(length=26), nullable=False),
    sa.Column('user_name', sa.String(length=100), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('hours_required', sa.Float(), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.Column('timestamp', sa.BigInteger(), nullable=False),
    sa.Column('hours_worked', sa.Float(), nullable=False),
    sa.Column('returned', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('task_log',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('timestamp', sa.BigInteger(), nullable=False),
    sa.Column('task_id', sa.String(length=26), nullable=False),
    sa.Column('task_name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('user_id', sa.String(length=26), nullable=False),
    sa.Column('user_name', sa.String(length=50), nullable=False),
    sa.Column('project_id', sa.String(length=26), nullable=False),
    sa.Column('project_name', sa.String(length=100), nullable=False),
    sa.Column('hours_spent_today', sa.Float(), nullable=False),
    sa.Column('task_status', sa.String(length=50), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
    sa.ForeignKeyConstraint(['task_id'], ['task.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('task_log')
    op.drop_table('task')
    op.drop_table('remote_days')
    op.drop_table('project_developers')
    op.drop_table('user')
    op.drop_table('project')
    # ### end Alembic commands ###