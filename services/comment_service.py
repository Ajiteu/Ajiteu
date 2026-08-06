"""댓글 비즈니스 로직."""

from extensions import db
from models.comment import Comment
from models.post import Post
from services import ServiceError
from utils.validators import validate_comment_content


def _comment_item(comment: Comment) -> dict:
    return {
        "id": comment.id,
        "content": comment.content,
        "image_url": comment.image_url,
        "parent_id": comment.parent_id,
        "author": {
            "id": comment.author.id,
            "nickname": comment.author.nickname,
            "profile_image": comment.author.profile_image,
        },
        "created_at": comment.created_at.isoformat() if comment.created_at else None,
    }


def list_comments(post_id: int) -> list[dict]:
    """특정 게시글의 댓글 목록 (대댓글 포함)."""
    post = db.session.get(Post, post_id)
    if not post:
        raise ServiceError("게시글을 찾을 수 없습니다.", 404)

    comments = (
        Comment.query.filter_by(post_id=post_id)
        .order_by(Comment.created_at.asc())
        .all()
    )
    return [_comment_item(comment) for comment in comments]


def create_comment(
    user_id: int,
    post_id: int,
    content: str,
    parent_id: int | None = None,
    image_url: str | None = None,
) -> dict:
    """댓글/대댓글 작성."""
    post = db.session.get(Post, post_id)
    if not post:
        raise ServiceError("게시글을 찾을 수 없습니다.", 404)

    image_url = (image_url or "").strip() or None
    content = validate_comment_content(content, image_url)

    if parent_id is not None:
        parent = db.session.get(Comment, parent_id)
        if not parent or parent.post_id != post_id:
            raise ServiceError("부모 댓글을 찾을 수 없습니다.", 404)

    comment = Comment(
        post_id=post_id,
        user_id=user_id,
        content=content,
        image_url=image_url,
        parent_id=parent_id,
    )
    post.comment_count += 1
    db.session.add(comment)
    db.session.commit()

    return {
        "id": comment.id,
        "content": comment.content,
        "image_url": comment.image_url,
        "parent_id": comment.parent_id,
    }


def update_comment(
    user_id: int,
    comment_id: int,
    post_id: int,
    content: str,
    image_url: str | None = None,
) -> dict:
    """댓글 수정 (작성자만)."""
    comment = db.session.get(Comment, comment_id)
    if not comment or comment.post_id != post_id:
        raise ServiceError("댓글을 찾을 수 없습니다.", 404)

    if comment.user_id != user_id:
        raise ServiceError("수정 권한이 없습니다.", 403)

    if image_url is not None:
        image_url = (image_url or "").strip() or None
    else:
        image_url = comment.image_url

    content = validate_comment_content(content, image_url)
    comment.content = content
    comment.image_url = image_url

    db.session.commit()
    return _comment_item(comment)


def delete_comment(user_id: int, comment_id: int, post_id: int | None = None) -> dict:
    """댓글 삭제 (작성자만)."""
    comment = db.session.get(Comment, comment_id)
    if not comment:
        raise ServiceError("댓글을 찾을 수 없습니다.", 404)

    if post_id is not None and comment.post_id != post_id:
        raise ServiceError("댓글을 찾을 수 없습니다.", 404)

    if comment.user_id != user_id:
        raise ServiceError("삭제 권한이 없습니다.", 403)

    post = db.session.get(Post, comment.post_id)
    if post and post.comment_count > 0:
        post.comment_count -= 1

    db.session.delete(comment)
    db.session.commit()
    return {"deleted": True}
