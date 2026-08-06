"""테스트용 초기 데이터."""

from extensions import db
from models.category import Category
from models.comment import Comment
from models.like import Like
from models.post import Post
from models.user import User
from services.category_service import DEFAULT_CATEGORIES, ensure_default_categories


def seed_if_empty() -> bool:
    """DB가 비어 있으면 테스트 계정·게시글을 넣습니다."""
    if User.query.first():
        ensure_default_categories()
        return False

    alice = User(
        username="alice",
        email="alice@example.com",
        nickname="닉네임",
        bio="햇살 좋은 날, 따뜻한 커피 한 잔과 함께 좋아하는 책을 읽는 시간이 참 행복해요",
    )
    alice.set_password("password123")
    bob = User(
        username="bob",
        email="bob@example.com",
        nickname="여행좋아",
        bio="여행과 사진을 좋아합니다.",
    )
    bob.set_password("password123")
    db.session.add_all([alice, bob])
    db.session.flush()

    for name, slug in DEFAULT_CATEGORIES:
        db.session.add(Category(name=name, slug=slug))
    db.session.flush()

    travel = Category.query.filter_by(slug="travel").first()
    food = Category.query.filter_by(slug="food").first()

    post1 = Post(
        user_id=alice.id,
        title="Community communities size test",
        content=(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit, "
            "sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
        ),
        category_id=travel.id if travel else None,
        like_count=156,
        comment_count=2,
    )
    post2 = Post(
        user_id=bob.id,
        title="제주 바다 사진 모음",
        content="사진 너무 이쁘네요!! 어디인가요?",
        category_id=travel.id if travel else None,
        like_count=42,
        comment_count=1,
    )
    post3 = Post(
        user_id=alice.id,
        title="감성 브런치 만들기",
        content="분위기 최고에요! 저도 저런 시간 보내고 싶어요^-^",
        category_id=food.id if food else None,
        like_count=28,
    )
    db.session.add_all([post1, post2, post3])
    db.session.flush()

    comment1 = Comment(
        post_id=post1.id, user_id=bob.id, content="사진 너무 이쁘네요!! 어디인가요?"
    )
    comment2 = Comment(
        post_id=post1.id,
        user_id=alice.id,
        content="분위기 최고에요! 저도 저런 시간 보내고 싶어요^-^",
        parent_id=None,
    )
    db.session.add_all([comment1, comment2])
    db.session.flush()

    reply = Comment(
        post_id=post1.id,
        user_id=bob.id,
        content="저도 공감해요!",
        parent_id=comment1.id,
    )
    db.session.add(reply)
    post1.comment_count = 3

    db.session.add(Like(post_id=post1.id, user_id=bob.id))
    db.session.add(Like(post_id=post1.id, user_id=alice.id))

    db.session.commit()
    return True
