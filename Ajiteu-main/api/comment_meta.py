"""댓글 이미지 부가 정보 — ajiteu/models.py 는 수정하지 않음."""

from __future__ import annotations

from ajiteu import db


class CommentMeta(db.Model):
    __tablename__ = "comment_meta"

    comment_id = db.Column(
        db.Integer,
        db.ForeignKey("comment.id", ondelete="CASCADE"),
        primary_key=True,
    )
    image_path = db.Column(db.String(500), nullable=True)


def get_comment_image(comment_id: int) -> str | None:
    meta = CommentMeta.query.get(comment_id)
    return meta.image_path if meta else None


def set_comment_image(comment_id: int, image_path: str | None) -> None:
    meta = CommentMeta.query.get(comment_id)
    if not image_path:
        if meta:
            db.session.delete(meta)
        return
    if meta is None:
        meta = CommentMeta(comment_id=comment_id, image_path=image_path)
        db.session.add(meta)
    else:
        meta.image_path = image_path
