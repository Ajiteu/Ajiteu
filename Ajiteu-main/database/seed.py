"""테스트용 초기 데이터 (Ajiteu User 모델 기준)."""

from __future__ import annotations

from datetime import datetime

from werkzeug.security import generate_password_hash

from ajiteu import db
from ajiteu.models import Post, User


def seed_if_empty() -> bool:
    """유저가 없으면 alice/bob 테스트 계정을 넣습니다."""
    if User.query.first():
        return False

    alice = User(
        username="alice",
        password=generate_password_hash("password123"),
        email="alice@example.com",
        nickname="앨리스",
        user_intro="테스트 계정입니다.",
    )
    bob = User(
        username="bob",
        password=generate_password_hash("password123"),
        email="bob@example.com",
        nickname="밥",
        user_intro="테스트 계정입니다.",
    )
    db.session.add_all([alice, bob])
    db.session.flush()

    now = datetime.utcnow()
    posts = [
        Post(
            content="첫 게시글입니다. 커뮤니티에 오신 것을 환영합니다!",
            create_date=now,
            user_id=alice.id,
        ),
        Post(
            content="오늘 날씨가 좋네요. 제주 바다 여행 사진을 공유하고 싶어요!",
            create_date=now,
            user_id=bob.id,
        ),
        Post(
            content="홈트 운동 루틴 추천합니다. 아침에 스트레칭부터!",
            create_date=now,
            user_id=alice.id,
        ),
        Post(
            content="감성 브런치 만들기 — 주말 음식 레시피",
            create_date=now,
            user_id=bob.id,
        ),
    ]
    db.session.add_all(posts)
    db.session.flush()

    from api.meta_models import PostMeta, infer_category

    for post in posts:
        db.session.add(
            PostMeta(
                post_id=post.id,
                view_count=0,
                category=infer_category(post.content),
            )
        )

    db.session.commit()
    return True
