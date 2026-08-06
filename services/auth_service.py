"""회원가입·로그인·프로필 비즈니스 로직."""

from flask_jwt_extended import create_access_token

from extensions import db
from models.post import Post
from models.user import User
from services import ServiceError


from utils.validators import (
    validate_bio,
    validate_email,
    validate_nickname,
    validate_password,
    validate_username,
)


def register(
    username: str,
    email: str,
    password: str,
    nickname: str = "",
    password_confirm: str = "",
) -> dict:
    """회원가입."""
    username = validate_username(username)
    email = validate_email(email)
    password = validate_password(password)

    if password_confirm and password != password_confirm:
        raise ServiceError("비밀번호 확인이 일치하지 않습니다.", 400)

    if not nickname:
        nickname = username
    else:
        nickname = validate_nickname(nickname)

    if User.query.filter_by(username=username).first():
        raise ServiceError("이미 사용 중인 아이디입니다.", 400)

    if User.query.filter_by(email=email).first():
        raise ServiceError("이미 사용 중인 이메일입니다.", 400)

    user = User(username=username, email=email, nickname=nickname)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return {
        "id": user.id,
        "username": user.username,
        "nickname": user.nickname,
    }


def login(login_id: str, password: str) -> dict:
    """로그인."""
    if not login_id or not password:
        raise ServiceError("login_id, password는 필수입니다.", 400)

    user = User.query.filter(
        (User.username == login_id)
        | (User.email == login_id)
        | (User.nickname == login_id)
    ).first()

    if not user or not user.check_password(password):
        raise ServiceError("아이디 또는 비밀번호가 올바르지 않습니다.", 401)

    token = create_access_token(identity=str(user.id))
    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "nickname": user.nickname,
            "bio": user.bio,
            "profile_image": user.profile_image,
        },
        "access_token": token,
    }


def get_me(user_id: int) -> dict:
    """로그인한 사용자 정보."""
    user = db.session.get(User, user_id)
    if not user:
        raise ServiceError("사용자를 찾을 수 없습니다.", 404)

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "nickname": user.nickname,
        "bio": user.bio,
        "profile_image": user.profile_image,
    }


def get_profile(user_id: int, viewer_id: int | None = None) -> dict:
    """공개 프로필 조회."""
    user = db.session.get(User, user_id)
    if not user:
        raise ServiceError("사용자를 찾을 수 없습니다.", 404)

    post_count = Post.query.filter_by(user_id=user_id).count()

    return {
        "id": user.id,
        "nickname": user.nickname,
        "bio": user.bio,
        "profile_image": user.profile_image,
        "post_count": post_count,
    }


def update_profile(
    user_id: int,
    bio: str | None = None,
    nickname: str | None = None,
    profile_image: str | None = None,
) -> dict:
    """내 프로필 수정."""
    user = db.session.get(User, user_id)
    if not user:
        raise ServiceError("사용자를 찾을 수 없습니다.", 404)

    if bio is not None:
        user.bio = validate_bio(bio)
    if nickname is not None:
        user.nickname = validate_nickname(nickname)
    if profile_image is not None:
        user.profile_image = profile_image.strip() or None

    db.session.commit()

    return {
        "nickname": user.nickname,
        "bio": user.bio,
        "profile_image": user.profile_image,
    }
