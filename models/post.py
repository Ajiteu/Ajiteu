"""Post 모델."""

from datetime import datetime

from sqlalchemy import Index

from extensions import db


class Post(db.Model):
    __tablename__ = "posts"
    __table_args__ = (
        Index("idx_posts_user", "user_id"),
        Index("idx_posts_created", "created_at"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    category_id = db.Column(
        db.Integer, db.ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500))
    like_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    author = db.relationship("User", backref="posts")
    category = db.relationship("Category", backref="posts")

    def to_dict(self, include_author: bool = True) -> dict:
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "content": self.content,
            "image_url": self.image_url,
            "like_count": self.like_count,
            "comment_count": self.comment_count,
            "view_count": self.view_count or 0,
            "category_id": self.category_id,
            "category": self.category.to_dict() if self.category else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_author and self.author:
            data["author"] = {
                "id": self.author.id,
                "username": self.author.username,
                "nickname": self.author.nickname,
            }
        return data
