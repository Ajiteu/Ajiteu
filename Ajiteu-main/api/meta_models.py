"""Post 부가 정보 (조회수·카테고리) — ajiteu/models.py 는 수정하지 않음."""

from __future__ import annotations

from ajiteu import db

CATEGORY_KEYWORDS = {
    "travel": ("여행", "바다", "제주", "부산", "휴가", "산", "캠핑"),
    "food": ("음식", "브런치", "맛", "요리", "카페", "먹", "레시피"),
    "exercise": ("운동", "홈트", "헬스", "런닝", "요가", "스트레칭"),
}


def infer_category(content: str) -> str:
    text = (content or "").lower()
    for slug, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return slug
    return "all"


class PostMeta(db.Model):
    __tablename__ = "post_meta"

    post_id = db.Column(
        db.Integer, db.ForeignKey("post.id", ondelete="CASCADE"), primary_key=True
    )
    view_count = db.Column(db.Integer, nullable=False, default=0)
    category = db.Column(db.String(20), nullable=False, default="all")


def get_or_create_meta(post_id: int, content: str = "") -> PostMeta:
    meta = PostMeta.query.get(post_id)
    if meta is None:
        meta = PostMeta(
            post_id=post_id,
            view_count=0,
            category=infer_category(content),
        )
        db.session.add(meta)
        db.session.commit()
    return meta
