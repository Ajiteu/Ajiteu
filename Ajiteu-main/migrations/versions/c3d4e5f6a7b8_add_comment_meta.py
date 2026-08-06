"""Add comment_meta table for comment images."""

from alembic import op
import sqlalchemy as sa


revision = "c3d4e5f6a7b8"
down_revision = "b1c2d3e4f5a6"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "comment_meta",
        sa.Column("comment_id", sa.Integer(), nullable=False),
        sa.Column("image_path", sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(["comment_id"], ["comment.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("comment_id"),
    )


def downgrade():
    op.drop_table("comment_meta")
