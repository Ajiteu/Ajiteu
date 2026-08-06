"""게시글 JSON API (세션 인증 + ajiteu 모델)."""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta

from flask import Blueprint, g, request
from werkzeug.utils import secure_filename

from ajiteu import db
from ajiteu.models import Comment, Post
from api.helpers import fail, ok, require_login
from api.meta_models import PostMeta, get_or_create_meta, infer_category

bp = Blueprint("api_posts", __name__, url_prefix="/api/posts")


def _format_date(value: datetime | None) -> str:
    if not value:
        return ""
    return value.strftime("%Y.%m.%d %H:%M")


def _first_image(path: str | None) -> str | None:
    if not path:
        return None
    first = path.split(",")[0].strip()
    return first or None


def _image_list(path: str | None) -> list[str]:
    if not path:
        return []
    return [item.strip() for item in path.split(",") if item.strip()]


def _title_from_content(content: str) -> str:
    snippet = (content or "").strip().replace("\n", " ")
    if len(snippet) > 40:
        return snippet[:40] + "..."
    return snippet or "제목 없음"


def _post_payload(post: Post, *, liked_by_me: bool = False) -> dict:
    meta = get_or_create_meta(post.id, post.content or "")
    return {
        "id": post.id,
        "user_id": post.user_id,
        "title": _title_from_content(post.content or ""),
        "content": post.content or "",
        "author": post.user.nickname if post.user else "알 수 없음",
        "created_at": _format_date(post.create_date),
        "created_date": _format_date(post.create_date),
        "like_count": len(post.liker) if post.liker is not None else 0,
        "comment_count": len(post.comment_set) if post.comment_set is not None else 0,
        "view_count": meta.view_count,
        "category": meta.category,
        "image_path": post.image_path,
        "image_url": _first_image(post.image_path),
        "images": _image_list(post.image_path),
        "liked_by_me": liked_by_me,
    }


def _card_payload(post: Post) -> dict:
    data = _post_payload(post, liked_by_me=_user_liked(post))
    data["excerpt"] = data["content"]
    return data


def _user_liked(post: Post) -> bool:
    if g.user is None or post.liker is None:
        return False
    return g.user in post.liker


def _apply_filters(query, *, category: str | None, search: str | None, mine: bool):
    if mine:
        if g.user is None:
            return None
        query = query.filter(Post.user_id == g.user.id)

    if search:
        pattern = f"%{search}%"
        query = query.filter(Post.content.ilike(pattern))

    if category and category not in ("all", ""):
        post_ids = [
            row.post_id
            for row in PostMeta.query.filter_by(category=category).all()
        ]
        if not post_ids:
            return query.filter(Post.id == -1)
        query = query.filter(Post.id.in_(post_ids))

    return query


@bp.get("")
def list_posts():
    category = (request.args.get("category") or "all").strip()
    search = (request.args.get("search") or request.args.get("q") or "").strip()
    mine = request.args.get("mine") in {"1", "true", "yes"}

    if mine:
        auth_error = require_login()
        if auth_error:
            return auth_error

    query = Post.query
    query = _apply_filters(query, category=category, search=search or None, mine=mine)
    if query is None:
        return fail("로그인이 필요합니다.", 401)

    page = max(int(request.args.get("page", 1)), 1)
    per_page = min(max(int(request.args.get("per_page", 10)), 1), 20)

    pagination = query.order_by(Post.create_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    items = [_card_payload(post) for post in pagination.items]
    return ok(
        {
            "items": items,
            "posts": items,
            "total": pagination.total,
            "page": page,
            "per_page": per_page,
            "pages": pagination.pages,
        }
    )


@bp.get("/mine")
def my_posts():
    auth_error = require_login()
    if auth_error:
        return auth_error

    posts = (
        Post.query.filter_by(user_id=g.user.id)
        .order_by(Post.create_date.desc())
        .all()
    )
    items = [_card_payload(post) for post in posts]
    return ok({"items": items, "posts": items, "total": len(items)})


@bp.get("/trending")
def trending_posts():
    limit = min(int(request.args.get("limit", 5)), 10)
    week_ago = datetime.utcnow() - timedelta(days=7)

    posts = Post.query.filter(Post.create_date >= week_ago).all()
    ranked = sorted(
        posts,
        key=lambda post: (
            len(post.liker) if post.liker is not None else 0,
            get_or_create_meta(post.id, post.content or "").view_count,
        ),
        reverse=True,
    )[:limit]

    items = [
        {
            "id": post.id,
            "title": _title_from_content(post.content or ""),
            "like_count": len(post.liker) if post.liker is not None else 0,
            "view_count": get_or_create_meta(post.id, post.content or "").view_count,
        }
        for post in ranked
    ]
    return ok({"items": items})


@bp.get("/<int:post_id>")
def get_post(post_id: int):
    post = Post.query.get_or_404(post_id)
    meta = get_or_create_meta(post.id, post.content or "")

    count_view = request.args.get("count_view", "1").lower() not in {"0", "false", "no"}
    if count_view:
        meta.view_count += 1
        db.session.commit()

    return ok(_post_payload(post, liked_by_me=_user_liked(post)))


@bp.post("")
def create_post():
    auth_error = require_login()
    if auth_error:
        return auth_error

    data = request.get_json(silent=True) or {}
    content = (data.get("content") or "").strip()
    image_path = (data.get("image_path") or data.get("image_url") or "").strip() or None

    if not content and not image_path:
        return fail("내용 또는 사진을 입력해주세요.", 400)

    post = Post(
        content=content or "(사진)",
        create_date=datetime.utcnow(),
        user_id=g.user.id,
        image_path=image_path,
    )
    db.session.add(post)
    db.session.flush()

    category = (data.get("category") or infer_category(content)).strip() or "all"
    db.session.add(
        PostMeta(post_id=post.id, view_count=0, category=category)
    )
    db.session.commit()

    return ok(_post_payload(post), 201)


@bp.put("/<int:post_id>")
def update_post(post_id: int):
    auth_error = require_login()
    if auth_error:
        return auth_error

    post = Post.query.get_or_404(post_id)
    if post.user_id != g.user.id:
        return fail("수정 권한이 없습니다.", 403)

    data = request.get_json(silent=True) or {}
    content = (data.get("content") or "").strip()
    image_path = data.get("image_path")
    if image_path is not None:
        post.image_path = (str(image_path).strip() or None)
    if content:
        post.content = content
    elif not post.image_path:
        return fail("내용 또는 사진을 입력해주세요.", 400)

    post.modify_date = datetime.utcnow()
    meta = get_or_create_meta(post.id, post.content or "")
    meta.category = (data.get("category") or infer_category(post.content or "")).strip() or "all"
    db.session.commit()

    return ok(_post_payload(post))


@bp.delete("/<int:post_id>")
def delete_post(post_id: int):
    auth_error = require_login()
    if auth_error:
        return auth_error

    post = Post.query.get_or_404(post_id)
    if post.user_id != g.user.id:
        return fail("삭제 권한이 없습니다.", 403)

    db.session.delete(post)
    db.session.commit()
    return ok({"deleted": True, "id": post_id})


@bp.post("/<int:post_id>/like")
def like_post(post_id: int):
    auth_error = require_login()
    if auth_error:
        return auth_error

    post = Post.query.get_or_404(post_id)
    if post.user_id == g.user.id:
        return fail("본인이 작성한 글은 추천할 수 없습니다.", 400)

    if g.user in post.liker:
        post.liker.remove(g.user)
        liked = False
    else:
        post.liker.append(g.user)
        liked = True
    db.session.commit()

    return ok(
        {
            "like_count": len(post.liker),
            "liked": liked,
            "liked_by_me": liked,
        }
    )


@bp.post("/upload")
def upload_image():
    auth_error = require_login()
    if auth_error:
        return auth_error

    file = request.files.get("file")
    if not file or not file.filename:
        return fail("이미지 파일이 필요합니다.", 400)

    ext = os.path.splitext(secure_filename(file.filename))[1].lower()
    if ext not in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
        return fail("이미지 파일만 업로드할 수 있습니다.", 400)

    upload_dir = os.path.join("ajiteu", "static", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{ext}"
    file.save(os.path.join(upload_dir, filename))

    url = f"/static/uploads/{filename}"
    return ok({"url": url, "image_path": url}, 201)
