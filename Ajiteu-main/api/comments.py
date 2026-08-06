"""댓글 JSON API."""

from __future__ import annotations

from datetime import datetime

from flask import Blueprint, g, request

from ajiteu import db
from ajiteu.models import Comment, Post
from api.comment_meta import get_comment_image, set_comment_image
from api.helpers import fail, ok, require_login

bp = Blueprint("api_comments", __name__, url_prefix="/api/posts")


def _comment_payload(comment: Comment) -> dict:
    image_path = get_comment_image(comment.id)
    return {
        "id": comment.id,
        "post_id": comment.post_id,
        "content": comment.content,
        "image_path": image_path,
        "image_url": image_path,
        "created_at": comment.create_date.isoformat() if comment.create_date else "",
        "author": {
            "id": comment.user.id if comment.user else None,
            "nickname": comment.user.nickname if comment.user else "알 수 없음",
        },
        "parent_id": None,
    }


@bp.get("/<int:post_id>/comments")
def list_comments(post_id: int):
    Post.query.get_or_404(post_id)
    comments = (
        Comment.query.filter_by(post_id=post_id)
        .order_by(Comment.create_date.asc())
        .all()
    )
    return ok([_comment_payload(comment) for comment in comments])


@bp.post("/<int:post_id>/comments")
def create_comment(post_id: int):
    auth_error = require_login()
    if auth_error:
        return auth_error

    post = Post.query.get_or_404(post_id)
    payload = request.get_json(silent=True) or {}
    content = (payload.get("content") or "").strip()
    image_path = (payload.get("image_path") or payload.get("image_url") or "").strip() or None

    if not content and not image_path:
        return fail("댓글 내용 또는 사진을 입력해주세요.", 400)

    comment = Comment(
        post_id=post.id,
        user_id=g.user.id,
        content=content or "(사진)",
        create_date=datetime.utcnow(),
    )
    db.session.add(comment)
    db.session.flush()
    set_comment_image(comment.id, image_path)
    db.session.commit()

    return ok(_comment_payload(comment), 201)
