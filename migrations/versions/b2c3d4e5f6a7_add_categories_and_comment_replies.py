"""add categories and comment replies

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-08-05 13:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "categories" not in tables:
        op.create_table(
            "categories",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=50), nullable=False),
            sa.Column("slug", sa.String(length=50), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("name"),
            sa.UniqueConstraint("slug"),
        )

    posts_cols = {column["name"] for column in inspector.get_columns("posts")}
    if "category_id" not in posts_cols:
        with op.batch_alter_table("posts", schema=None) as batch_op:
            batch_op.add_column(
                sa.Column("category_id", sa.Integer(), nullable=True)
            )
            batch_op.create_foreign_key(
                "fk_posts_category_id",
                "categories",
                ["category_id"],
                ["id"],
                ondelete="SET NULL",
            )

    comments_cols = {column["name"] for column in inspector.get_columns("comments")}
    if "parent_id" not in comments_cols:
        with op.batch_alter_table("comments", schema=None) as batch_op:
            batch_op.add_column(
                sa.Column("parent_id", sa.Integer(), nullable=True)
            )
            batch_op.create_foreign_key(
                "fk_comments_parent_id",
                "comments",
                ["parent_id"],
                ["id"],
                ondelete="CASCADE",
            )


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    comments_cols = {column["name"] for column in inspector.get_columns("comments")}
    posts_cols = {column["name"] for column in inspector.get_columns("posts")}

    if "parent_id" in comments_cols:
        with op.batch_alter_table("comments", schema=None) as batch_op:
            batch_op.drop_constraint("fk_comments_parent_id", type_="foreignkey")
            batch_op.drop_column("parent_id")

    if "category_id" in posts_cols:
        with op.batch_alter_table("posts", schema=None) as batch_op:
            batch_op.drop_constraint("fk_posts_category_id", type_="foreignkey")
            batch_op.drop_column("category_id")

    if "categories" in inspector.get_table_names():
        op.drop_table("categories")
