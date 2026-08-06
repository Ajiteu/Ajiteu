"""카테고리 API."""

from flask import Blueprint

from views.utils import handle_service
from services import category_service

category_api = Blueprint("category_api", __name__, url_prefix="/api/categories")


@category_api.get("")
def list_categories():
    """카테고리 목록."""
    return handle_service(category_service.list_categories)
