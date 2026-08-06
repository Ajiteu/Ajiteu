"""게시글 CRUD 비즈니스 로직."""

from datetime import datetime, timedelta

from extensions import db
from models.comment import Comment
from models.like import Like
from models.post import Post
from services import ServiceError
from services.category_service import get_category_by_slug, validate_category_id
from utils.validators import validate_post_content, validate_post_title


def _format_date(iso_value: str | None) -> str | None:
    if not iso_value:
        return None
    try:
        dt = datetime.fromisoformat(iso_value)
        return dt.strftime("%Y.%m.%d %H:%M")
    except ValueError:
        return iso_value


def _list_item(post: Post) -> dict:
    created = post.created_at.isoformat() if post.created_at else None
    return {
        "id": post.id,
        "user_id": post.user_id,
        "title": post.title,
        "content": post.content,
        "image_url": post.image_url,
        "like_count": post.like_count,
        "comment_count": post.comment_count,
        "view_count": post.view_count or 0,
        "category_id": post.category_id,
        "category": post.category.to_dict() if post.category else None,
        "author": {
            "id": post.author.id,
            "nickname": post.author.nickname,
            "profile_image": post.author.profile_image,
        },
        "created_at": created,
        "created_date": _format_date(created),
    }


def _detail(post: Post, user_id: int | None = None) -> dict:
    data = _list_item(post)
    data["liked_by_me"] = False
    if user_id is not None:
        data["liked_by_me"] = (
            Like.query.filter_by(post_id=post.id, user_id=user_id).first()
            is not None
        )
    return data


def _auto_title(title: str, content: str) -> str:
    title = (title or "").strip()
    if title:
        return validate_post_title(title)

    snippet = content.strip().replace("\n", " ")
    if not snippet:
        return validate_post_title("")

    if len(snippet) > 50:
        return snippet[:50] + "..."
    return snippet


def list_posts(
    page: int = 1,
    per_page: int = 10,
    query: str | None = None,
    category_slug: str | None = None,
    user_id: int | None = None,
) -> dict:
    """페이지네이션된 게시글 목록."""
    page = max(page, 1)
    per_page = min(max(per_page, 1), 50)

    posts_query = Post.query
    search = (query or "").strip()
    if search:
        pattern = f"%{search}%"
        posts_query = posts_query.filter(
            db.or_(Post.title.ilike(pattern), Post.content.ilike(pattern))
        )

    if category_slug:
        category = get_category_by_slug(category_slug)
        if category:
            keyword = category.name
            pattern = f"%{keyword}%"
            comment_post_ids = (
                db.session.query(Comment.post_id)
                .filter(Comment.content.ilike(pattern))
                .distinct()
            )
            posts_query = posts_query.filter(
                db.or_(
                    Post.title.ilike(pattern),
                    Post.content.ilike(pattern),
                    Post.id.in_(comment_post_ids),
                )
            )

    if user_id is not None:
        posts_query = posts_query.filter_by(user_id=user_id)

    pagination = posts_query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return {
        "items": [_list_item(post) for post in pagination.items],
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
        "query": search or None,
        "category": category_slug,
    }


def get_trending(limit: int = 5) -> list[dict]:
    """주간 트렌드 (최근 7일 + 조회수 순)."""
    limit = min(max(limit, 1), 20)
    week_ago = datetime.utcnow() - timedelta(days=7)
    posts = (
        Post.query.filter(Post.created_at >= week_ago)
        .order_by(Post.view_count.desc(), Post.created_at.desc())
        .limit(limit)
        .all()
    )
    if not posts:
        posts = (
            Post.query.order_by(Post.view_count.desc(), Post.created_at.desc())
            .limit(limit)
            .all()
        )
    return [_list_item(post) for post in posts]


def get_post(
    post_id: int, user_id: int | None = None, increment_view: bool = True
) -> dict:
    """게시글 상세."""
    post = db.session.get(Post, post_id)
    if not post:
        raise ServiceError("게시글을 찾을 수 없습니다.", 404)

    if increment_view:
        post.view_count = (post.view_count or 0) + 1
        db.session.commit()
    return _detail(post, user_id)


def create_post(
    user_id: int,
    title: str,
    content: str,
    image_url: str | None = None,
    category_id: int | None = None,
) -> dict:
    """게시글 작성."""
    image_url = (image_url or "").strip() or None
    content = (content or "").strip()

    if not content and not image_url:
        raise ServiceError("내용 또는 image_url이 필요합니다.", 400)

    title = _auto_title(title, content or "사진 게시글")
    content = validate_post_content(content) if content else " "
    category_id = validate_category_id(category_id)

    post = Post(
        user_id=user_id,
        title=title,
        content=content,
        image_url=image_url or None,
        category_id=category_id,
    )
    db.session.add(post)
    db.session.commit()

    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
    }


def update_post(
    user_id: int,
    post_id: int,
    title: str,
    content: str,
    image_url: str | None = None,
    category_id: int | None = None,
) -> dict:
    """게시글 수정 (작성자만)."""
    post = db.session.get(Post, post_id)
    if not post:
        raise ServiceError("게시글을 찾을 수 없습니다.", 404)

    if post.user_id != user_id:
        raise ServiceError("수정 권한이 없습니다.", 403)

    title = _auto_title(title, content)
    content = validate_post_content(content)

    post.title = title
    post.content = content
    if image_url is not None:
        post.image_url = image_url or None
    if category_id is not None:
        post.category_id = validate_category_id(category_id)

    db.session.commit()

    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
    }


def delete_post(user_id: int, post_id: int) -> dict:
    """게시글 삭제 (작성자만)."""
    post = db.session.get(Post, post_id)
    if not post:
        raise ServiceError("게시글을 찾을 수 없습니다.", 404)

    if post.user_id != user_id:
        raise ServiceError("삭제 권한이 없습니다.", 403)

    db.session.delete(post)
    db.session.commit()
    return {"deleted": True}
