"""add view_count to post

Revision ID: a1b2c3d4e5f6
Revises: c721eb1ee6f2
Create Date: 2026-08-10 15:55:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'a1b2c3d4e5f6'
down_revision = 'c721eb1ee6f2'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('view_count', sa.Integer(), nullable=False, server_default='0')
        )


def downgrade():
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.drop_column('view_count')
