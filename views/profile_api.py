"""프로필 API."""

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from views.utils import get_optional_user_id, handle_service
from services import auth_service

profile_api = Blueprint("profile_api", __name__, url_prefix="/api/profile")


@profile_api.get("/<int:user_id>")
def get_profile(user_id: int):
    """프로필 조회."""
    viewer_id = get_optional_user_id()
    return handle_service(lambda: auth_service.get_profile(user_id, viewer_id))


@profile_api.put("")
@jwt_required()
def update_profile():
    """내 프로필 수정."""
    data = request.get_json(silent=True) or {}
    current_user_id = int(get_jwt_identity())
    return handle_service(
        lambda: auth_service.update_profile(
            current_user_id,
            data.get("bio"),
            data.get("nickname"),
            data.get("profile_image"),
        )
    )
