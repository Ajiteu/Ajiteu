"""Comment 모델."""

from datetime import datetime

from sqlalchemy import Index

from extensions import db


class Comment(db.Model):
    __tablename__ = "comments"
    __table_args__ = (Index("idx_comments_post", "post_id"),)

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(
        db.Integer, db.ForeignKey("posts.id", ondelete="CASCADE"), nullable=False
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    content = db.Column(db.String(500), nullable=False)
    image_url = db.Column(db.String(500), nullable=True)
    parent_id = db.Column(
        db.Integer, db.ForeignKey("comments.id", ondelete="CASCADE"), nullable=True
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    author = db.relationship("User")
    post = db.relationship("Post", backref="comments")
    parent = db.relationship("Comment", remote_side=[id], backref="replies")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "post_id": self.post_id,
            "user_id": self.user_id,
            "content": self.content,
            "image_url": self.image_url,
            "parent_id": self.parent_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "author": {
                "id": self.author.id,
                "username": self.author.username,
                "nickname": self.author.nickname,
            }
            if self.author
            else None,
        }
