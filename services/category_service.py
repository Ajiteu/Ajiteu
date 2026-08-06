"""카테고리 비즈니스 로직."""

from extensions import db
from models.category import Category
from services import ServiceError


DEFAULT_CATEGORIES = [
    ("여행", "travel"),
    ("운동", "exercise"),
    ("음식", "food"),
]


def ensure_default_categories() -> None:
    """기본 카테고리가 없으면 생성."""
    if Category.query.first():
        return

    for name, slug in DEFAULT_CATEGORIES:
        db.session.add(Category(name=name, slug=slug))
    db.session.commit()


def list_categories() -> list[dict]:
    """카테고리 목록."""
    ensure_default_categories()
    categories = Category.query.order_by(Category.id.asc()).all()
    return [category.to_dict() for category in categories]


def get_category_by_slug(slug: str) -> Category | None:
    """slug로 카테고리 조회."""
    return Category.query.filter_by(slug=slug).first()


def validate_category_id(category_id: int | None) -> int | None:
    """유효한 category_id인지 확인."""
    if category_id is None:
        return None

    category = db.session.get(Category, category_id)
    if not category:
        raise ServiceError("카테고리를 찾을 수 없습니다.", 400)
    return category_id
