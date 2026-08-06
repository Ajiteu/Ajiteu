"""게시글 CRUD API."""

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from views.utils import get_optional_user_id, handle_service
from services import post_service

post_bp = Blueprint("post_api", __name__, url_prefix="/api/posts")


@post_bp.get("/mine")
@jwt_required()
def my_posts():
    """내가 쓴 글."""
    user_id = int(get_jwt_identity())
    page = max(int(request.args.get("page", 1)), 1)
    per_page = min(int(request.args.get("per_page", 10)), 50)
    return handle_service(
        lambda: post_service.list_posts(page, per_page, user_id=user_id)
    )


@post_bp.get("/trending")
def trending_posts():
    """주간 트렌드."""
    limit = min(int(request.args.get("limit", 5)), 20)
    return handle_service(lambda: {"items": post_service.get_trending(limit)})


@post_bp.get("")
def list_posts():
    """게시글 목록."""
    page = max(int(request.args.get("page", 1)), 1)
    per_page = min(int(request.args.get("per_page", 10)), 50)
    query = (request.args.get("q") or "").strip() or None
    category = (request.args.get("category") or "").strip() or None
    return handle_service(
        lambda: post_service.list_posts(page, per_page, query, category)
    )


@post_bp.get("/<int:post_id>")
def get_post(post_id: int):
    """게시글 상세."""
    user_id = get_optional_user_id()
    count_view = request.args.get("count_view", "1").lower() not in {"0", "false", "no"}
    return handle_service(
        lambda: post_service.get_post(post_id, user_id, increment_view=count_view)
    )


@post_bp.post("")
@jwt_required()
def create_post():
    """게시글 작성."""
    data = request.get_json(silent=True) or {}
    user_id = int(get_jwt_identity())
    category_id = data.get("category_id")
    return handle_service(
        lambda: post_service.create_post(
            user_id,
            (data.get("title") or "").strip(),
            (data.get("content") or "").strip(),
            (data.get("image_url") or "").strip() or None,
            int(category_id) if category_id else None,
        ),
        201,
    )


@post_bp.put("/<int:post_id>")
@jwt_required()
def update_post(post_id: int):
    """게시글 수정."""
    data = request.get_json(silent=True) or {}
    user_id = int(get_jwt_identity())
    category_id = data.get("category_id")
    return handle_service(
        lambda: post_service.update_post(
            user_id,
            post_id,
            (data.get("title") or "").strip(),
            (data.get("content") or "").strip(),
            data.get("image_url"),
            int(category_id) if category_id is not None else None,
        )
    )


@post_bp.delete("/<int:post_id>")
@jwt_required()
def delete_post(post_id: int):
    """게시글 삭제."""
    user_id = int(get_jwt_identity())
    return handle_service(lambda: post_service.delete_post(user_id, post_id))
