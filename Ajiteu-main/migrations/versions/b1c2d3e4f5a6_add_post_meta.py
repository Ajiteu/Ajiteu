"""Increase revision ID: b1c2d3e4f5a6

Add post_meta table for view_count and category.

"""
from alembic import op
import sqlalchemy as sa


revision = 'b1c2d3e4f5a6'
down_revision = 'a3f3bbc30d00'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'post_meta',
        sa.Column('post_id', sa.Integer(), nullable=False),
        sa.Column('view_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('category', sa.String(length=20), nullable=False, server_default='all'),
        sa.ForeignKeyConstraint(['post_id'], ['post.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('post_id'),
    )


def downgrade():
    op.drop_table('post_meta')
