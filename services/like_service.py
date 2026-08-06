"""좋아요 비즈니스 로직."""

from extensions import db
from models.like import Like
from models.post import Post
from services import ServiceError


def add_like(user_id: int, post_id: int) -> dict:
    """좋아요 추가."""
    post = db.session.get(Post, post_id)
    if not post:
        raise ServiceError("게시글을 찾을 수 없습니다.", 404)

    existing = Like.query.filter_by(post_id=post_id, user_id=user_id).first()
    if existing:
        raise ServiceError("이미 좋아요한 게시글입니다.", 400)

    db.session.add(Like(post_id=post_id, user_id=user_id))
    post.like_count += 1
    db.session.commit()

    return {
        "liked": True,
        "like_count": post.like_count,
    }


def remove_like(user_id: int, post_id: int) -> dict:
    """좋아요 취소."""
    post = db.session.get(Post, post_id)
    if not post:
        raise ServiceError("게시글을 찾을 수 없습니다.", 404)

    like = Like.query.filter_by(post_id=post_id, user_id=user_id).first()
    if not like:
        raise ServiceError("좋아요 내역이 없습니다.", 404)

    if post.like_count > 0:
        post.like_count -= 1

    db.session.delete(like)
    db.session.commit()

    return {
        "liked": False,
        "like_count": post.like_count,
    }
