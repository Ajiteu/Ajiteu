"""add comment image_url

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-08-05 13:15:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = "c3d4e5f6a7b8"
down_revision = "b2c3d4e5f6a7"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    comments_cols = {column["name"] for column in inspector.get_columns("comments")}

    if "image_url" not in comments_cols:
        with op.batch_alter_table("comments", schema=None) as batch_op:
            batch_op.add_column(sa.Column("image_url", sa.String(length=500), nullable=True))


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    comments_cols = {column["name"] for column in inspector.get_columns("comments")}

    if "image_url" in comments_cols:
        with op.batch_alter_table("comments", schema=None) as batch_op:
            batch_op.drop_column("image_url")
