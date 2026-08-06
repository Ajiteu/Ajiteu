"""add post view_count

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-08-05 14:40:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = "d4e5f6a7b8c9"
down_revision = "c3d4e5f6a7b8"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    posts_cols = {column["name"] for column in inspector.get_columns("posts")}

    if "view_count" not in posts_cols:
        with op.batch_alter_table("posts", schema=None) as batch_op:
            batch_op.add_column(
                sa.Column("view_count", sa.Integer(), nullable=False, server_default="0")
            )


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    posts_cols = {column["name"] for column in inspector.get_columns("posts")}

    if "view_count" in posts_cols:
        with op.batch_alter_table("posts", schema=None) as batch_op:
            batch_op.drop_column("view_count")
