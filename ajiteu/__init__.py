from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from ajiteu.filter import format_datetime           #filter추가
import config
# from flask_login import LoginManager  # 808 이 줄 추가

db = SQLAlchemy()
migrate = Migrate()
# login_manager = LoginManager()  # 808 이 줄 추가

def create_app():
    app = Flask(__name__)       
    app.config.from_object(config)
  
    #ORM 초기화 
    from . import models
    db.init_app(app)
    migrate.init_app(app, db)

    #  sinae 812 게시물 한번 생성
    @app.cli.command()
    def init_posts():
        """샘플 게시글 생성"""
        from ajiteu.data.sample_posts import init_sample_posts
        init_sample_posts()


    # # 808 Flask-Login 초기화 (이 부분 추가)
    # login_manager.init_app(app)
    # login_manager.login_view = 'auth.login'
    # # user_loader 콜백 추가 (이 부분)
    # @login_manager.user_loader
    # def load_user(user_id):
    #     from .models import User
    #     return User.query.get(int(user_id))

    app.jinja_env.filters['datetime'] = format_datetime         #806추가

    from .views import main_views, post_api, reply_api, comment_api, auth_views, profile
    app.register_blueprint(main_views.bp)
    app.register_blueprint(auth_views.bp)
    app.register_blueprint(post_api.bp)
    app.register_blueprint(reply_api.bp)
    app.register_blueprint(comment_api.bp)
    app.register_blueprint(profile.bp)

    return app