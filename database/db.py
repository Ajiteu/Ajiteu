"""데이터베이스 연결."""

import os

from dotenv import load_dotenv
from flask import Flask
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine

from extensions import db

from pathlib import Path

load_dotenv(".env")
load_dotenv("env")

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = BASE_DIR / "instance" / "app.db"


def get_database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if url and url != "sqlite:///app.db":
        return url

    DEFAULT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{DEFAULT_DB_PATH.as_posix()}"


@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record) -> None:
    """SQLite에서 FK 제약을 활성화합니다."""
    if dbapi_connection.__class__.__module__.startswith("sqlite3"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def ping() -> bool:
    """DB 연결 테스트 (SELECT 1)."""
    engine = create_engine(get_database_url())
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return True


def init_db(app: Flask) -> None:
    """앱 컨텍스트에서 테이블을 준비합니다."""
    from database.seed import seed_if_empty

    with app.app_context():
        if app.config.get("TESTING"):
            db.create_all()
        else:
            from flask_migrate import upgrade

            try:
                upgrade()
            except Exception as exc:
                app.logger.warning(
                    "DB migration failed, falling back to create_all: %s", exc
                )
                db.create_all()

        if not app.config.get("TESTING") and seed_if_empty():
            app.logger.info("테스트 계정 생성: alice / password123, bob / password123")

        from services.category_service import ensure_default_categories

        ensure_default_categories()
