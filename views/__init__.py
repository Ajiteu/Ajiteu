"""API Blueprint 등록."""

from views.utils import fail


def register_api(app):
    """모든 API Blueprint를 Flask 앱에 등록합니다."""
    from api.auth_api import auth_bp
    from api.comment_api import comment_api
    from api.like_api import like_api
    from api.post_api import post_bp
    from api.profile_api import profile_api

    app.register_blueprint(auth_bp)
    app.register_blueprint(post_bp)
    app.register_blueprint(comment_api)
    app.register_blueprint(like_api)
    app.register_blueprint(profile_api)

    @app.errorhandler(400)
    def bad_request(error):
        return fail(getattr(error, "description", "잘못된 요청입니다."), 400)

    @app.errorhandler(404)
    def not_found(error):
        return fail("요청한 리소스를 찾을 수 없습니다.", 404)
