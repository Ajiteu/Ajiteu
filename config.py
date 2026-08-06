"""Flask 앱 설정 (SECRET_KEY, DATABASE_URL 등)."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(".env")

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = BASE_DIR / "instance" / "ajiteu.db"


def get_database_url() -> str:
    """환경변수 DATABASE_URL이 있으면 사용, 없으면 프로젝트 instance/ SQLite를 씁니다.

    상대 경로(sqlite:///instance/..)는 Windows/OneDrive에서 실패하기 쉬워
    SQLite일 때는 가능하면 절대 경로로 바꿉니다.
    """
    DEFAULT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    url = os.environ.get("DATABASE_URL")

    if not url:
        return f"sqlite:///{DEFAULT_DB_PATH.as_posix()}"

    # sqlite:///상대경로 → 절대경로로 변환
    if url.startswith("sqlite:///") and not url.startswith("sqlite:////"):
        raw = url.removeprefix("sqlite:///")
        # Windows 절대경로(C:/...) 또는 이미 절대면 유지
        path = Path(raw)
        if not path.is_absolute():
            path = (BASE_DIR / path).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{path.as_posix()}"

    return url


# ajiteu/__init__.py 가 app.config.from_object(config) 로 읽음 → 모듈 상단 대문자 변수
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
SQLALCHEMY_DATABASE_URI = get_database_url()
SQLALCHEMY_TRACK_MODIFICATIONS = False

# 업로드 (post_api 등에서 사용)
UPLOAD_FOLDER = str(BASE_DIR / "ajiteu" / "static" / "uploads")
MAX_CONTENT_LENGTH = 5 * 1024 * 1024
