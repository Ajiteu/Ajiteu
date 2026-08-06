"""현재 로그인 사용자 API."""

from __future__ import annotations

from flask import Blueprint, g, request

from ajiteu import db
from api.helpers import fail, ok, require_login

bp = Blueprint("api_users", __name__, url_prefix="/api")


def _user_payload(user):
    return {
        "id": user.id,
        "username": user.username,
        "nickname": user.nickname,
        "email": user.email,
        "bio": user.user_intro or "",
        "profile_image": user.image_path,
    }


@bp.get("/me")
def me():
    auth_error = require_login()
    if auth_error:
        return auth_error

    return ok(_user_payload(g.user))


@bp.put("/profile")
def update_profile():
    auth_error = require_login()
    if auth_error:
        return auth_error

    data = request.get_json(silent=True) or {}
    nickname = (data.get("nickname") or "").strip()
    bio = (data.get("bio") or "").strip()
    profile_image = (
        data.get("profile_image") or data.get("image_path") or data.get("image_url") or ""
    ).strip() or None

    if not nickname:
        return fail("닉네임을 입력해주세요.", 400)

    g.user.nickname = nickname
    g.user.user_intro = bio
    if profile_image is not None:
        g.user.image_path = profile_image
    db.session.commit()

    return ok(_user_payload(g.user))
