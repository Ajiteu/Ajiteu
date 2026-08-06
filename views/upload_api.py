"""이미지 업로드 API."""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from views.utils import fail, handle_service
from services import upload_service

upload_api = Blueprint("upload_api", __name__, url_prefix="/api")


@upload_api.post("/upload")
@jwt_required()
def upload_image():
    """이미지 파일 업로드."""
    file = request.files.get("file")
    if not file:
        return fail("file 필드가 필요합니다.", 400)

    return handle_service(lambda: upload_service.upload_image(file), 201)
