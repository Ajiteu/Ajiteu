"""팀 프로젝트 app.py에 붙일 API 등록 모듈.

사용 예:
    from flask import Flask
    from config import Config
    from register_api import register_codingfive_api

    app = Flask(__name__)
    app.config.from_object(Config)
    register_codingfive_api(app)
"""

from flask_jwt_extended import JWTManager

from database.db import init_db
from extensions import db, jwt, migrate
from views.utils import fail

import models  # noqa: F401


def _register_jwt_handlers(jwt_manager: JWTManager) -> None:
    @jwt_manager.unauthorized_loader
    def missing_token(reason):
        return fail("로그인이 필요합니다.", 401)

    @jwt_manager.invalid_token_loader
    def invalid_token(reason):
        return fail("유효하지 않은 토큰입니다.", 401)

    @jwt_manager.expired_token_loader
    def expired_token(jwt_header, jwt_payload):
        return fail("토큰이 만료되었습니다.", 401)


def register_codingfive_api(app, *, init_database: bool = True) -> None:
    """DB·JWT·Blueprint를 Flask 앱에 한 번에 연결합니다.

    app.config.from_object(Config) 는 호출 전에 app.py에서 설정해 주세요.
    """
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    _register_jwt_handlers(jwt)

    if init_database and not app.config.get("TESTING"):
        init_db(app)

    from views.auth_api import auth_bp
    from views.category_api import category_api
    from views.comment_api import comment_api
    from views.like_api import like_api
    from views.post_api import post_bp
    from views.profile_api import profile_api
    from views.upload_api import upload_api

    app.register_blueprint(auth_bp)
    app.register_blueprint(post_bp)
    app.register_blueprint(comment_api)
    app.register_blueprint(like_api)
    app.register_blueprint(profile_api)
    app.register_blueprint(category_api)
    app.register_blueprint(upload_api)
