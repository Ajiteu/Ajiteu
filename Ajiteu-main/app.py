"""Ajiteu Flask 진입점."""

from ajiteu import create_app, db
from api.comments import bp as comments_api_bp
from api.meta_models import PostMeta
from api.posts import bp as posts_api_bp
from api.users import bp as users_api_bp


def register_api(app):
    app.register_blueprint(posts_api_bp)
    app.register_blueprint(comments_api_bp)
    app.register_blueprint(users_api_bp)

    with app.app_context():
        db.create_all()


app = create_app()
register_api(app)

if __name__ == "__main__":
    app.run(debug=True)
