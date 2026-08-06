"""회원가입·로그인 API."""

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from views.utils import handle_service
from services import auth_service

auth_bp = Blueprint("auth_api", __name__, url_prefix="/api")


@auth_bp.post("/register")
def register():
    """회원가입."""
    data = request.get_json(silent=True) or {}
    return handle_service(
        lambda: auth_service.register(
            (data.get("username") or "").strip().lower(),
            (data.get("email") or "").strip().lower(),
            data.get("password") or "",
            (data.get("nickname") or "").strip(),
            data.get("password_confirm") or "",
        ),
        201,
    )


@auth_bp.post("/login")
def login():
    """로그인."""
    data = request.get_json(silent=True) or {}
    return handle_service(
        lambda: auth_service.login(
            (data.get("login_id") or "").strip().lower(),
            data.get("password") or "",
        )
    )


@auth_bp.get("/me")
@jwt_required()
def me():
    """내 정보."""
    user_id = int(get_jwt_identity())
    return handle_service(lambda: auth_service.get_me(user_id))
