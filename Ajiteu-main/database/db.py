"""데이터베이스 연결 헬퍼."""

from __future__ import annotations

from dotenv import load_dotenv
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine

load_dotenv(".env")


def get_database_url() -> str:
    """config와 동일하게 SQLite는 절대 경로를 우선합니다."""
    from config import get_database_url as _config_url

    return _config_url()


@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record) -> None:
    """SQLite에서 FK 제약을 켭니다."""
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
