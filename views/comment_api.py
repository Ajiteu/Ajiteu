"""댓글 API."""

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from views.utils import handle_service
from services import comment_service

comment_api = Blueprint("comment_api", __name__, url_prefix="/api")


@comment_api.get("/posts/<int:post_id>/comments")
def list_comments(post_id: int):
    """댓글 목록."""
    return handle_service(lambda: comment_service.list_comments(post_id))


@comment_api.post("/posts/<int:post_id>/comments")
@jwt_required()
def create_comment(post_id: int):
    """댓글 작성."""
    data = request.get_json(silent=True) or {}
    user_id = int(get_jwt_identity())
    return handle_service(
        lambda: comment_service.create_comment(
            user_id,
            post_id,
            (data.get("content") or "").strip(),
            int(data["parent_id"]) if data.get("parent_id") else None,
            (data.get("image_url") or "").strip() or None,
        ),
        201,
    )


@comment_api.put("/posts/<int:post_id>/comments/<int:comment_id>")
@jwt_required()
def update_comment(post_id: int, comment_id: int):
    """댓글 수정 (작성자만)."""
    data = request.get_json(silent=True) or {}
    user_id = int(get_jwt_identity())
    return handle_service(
        lambda: comment_service.update_comment(
            user_id,
            comment_id,
            post_id,
            (data.get("content") or "").strip(),
            data.get("image_url") if "image_url" in data else None,
        )
    )


@comment_api.delete("/posts/<int:post_id>/comments/<int:comment_id>")
@jwt_required()
def delete_comment(post_id: int, comment_id: int):
    """댓글 삭제 (작성자만)."""
    user_id = int(get_jwt_identity())
    return handle_service(
        lambda: comment_service.delete_comment(user_id, comment_id, post_id)
    )
