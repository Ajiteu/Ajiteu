"""파일 업로드 비즈니스 로직."""

from pathlib import Path

from flask import current_app
from werkzeug.datastructures import FileStorage

from utils.file_upload import save_upload


def upload_image(file: FileStorage) -> dict:
    """이미지 업로드 후 공개 URL 반환."""
    upload_folder = Path(current_app.root_path) / current_app.config["UPLOAD_FOLDER"]
    url = save_upload(file, upload_folder)
    return {"url": url}
