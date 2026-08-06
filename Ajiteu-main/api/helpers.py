"""API 공통 헬퍼 (세션 인증)."""

from __future__ import annotations

from flask import g, jsonify


def ok(data=None, status=200):
    payload = {"ok": True, "data": data}
    if isinstance(data, dict) and "posts" in data:
        payload["posts"] = data["posts"]
    elif isinstance(data, list):
        payload["posts"] = data
    return jsonify(payload), status


def fail(message: str, status=400):
    return jsonify({"ok": False, "message": message}), status


def require_login():
    if g.user is None:
        return fail("로그인이 필요합니다.", 401)
    return None
