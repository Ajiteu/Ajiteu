"""팀 프로젝트 app.py에 붙일 API 등록 모듈.

사용 예:
    from flask import Flask
    from config import Config
    from register_api import register_codingfive_api

    app = Flask(__name__)
    app.config.from_object(Config)
    register_codingfive_api(app)
"""

from ajiteu import create_app, db, jwt, migrate
from ajiteu.views.utils import fail


def _register_jwt_handlers(jwt_manager):
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
        with app.app_context():
            db.create_all()

    from ajiteu.views.auth_views import api_bp as auth_api_bp
    from ajiteu.views.comment_api import api_bp as comment_api_bp
    from ajiteu.views.post_api import api_bp as post_api_bp

    app.register_blueprint(auth_api_bp)
    app.register_blueprint(post_api_bp)
    app.register_blueprint(comment_api_bp)


def create_codingfive_app():
    """ajiteu 앱 팩토리 래퍼."""
    return create_app()
