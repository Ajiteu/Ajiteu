"""좋아요 API."""

from flask import Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required

from views.utils import handle_service
from services import like_service

like_api = Blueprint("like_api", __name__, url_prefix="/api")


@like_api.post("/posts/<int:post_id>/like")
@jwt_required()
def like_post(post_id: int):
    """좋아요."""
    user_id = int(get_jwt_identity())
    return handle_service(lambda: like_service.add_like(user_id, post_id))


@like_api.delete("/posts/<int:post_id>/like")
@jwt_required()
def unlike_post(post_id: int):
    """좋아요 취소."""
    user_id = int(get_jwt_identity())
    return handle_service(lambda: like_service.remove_like(user_id, post_id))
