"""API 공통 응답 형식."""

from flask import jsonify, request
from flask_jwt_extended import decode_token

from services import ServiceError


def ok(data=None, status=200):
    return jsonify({"ok": True, "data": data}), status


def fail(message: str, status=400):
    return jsonify({"ok": False, "message": message}), status


def get_optional_user_id() -> int | None:
    """유효한 JWT가 있으면 user_id, 없거나 만료·무효면 None."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ", 1)[1].strip()
    if not token:
        return None

    try:
        payload = decode_token(token)
        return int(payload["sub"])
    except Exception:
        return None


def handle_service(callable_fn, success_status=200):
    """서비스 호출 → JSON 응답 변환."""
    try:
        data = callable_fn()
        return ok(data, success_status)
    except ServiceError as exc:
        return fail(exc.message, exc.status)
