from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)       
    app.config.from_object(config)
  
    #ORM 초기화 
    from . import models
    db.init_app(app)
    migrate.init_app(app, db)

    from .views import main_views, post_api, reply_api, comment_api, auth_views
    app.register_blueprint(main_views.bp)
    app.register_blueprint(auth_views.bp)
    app.register_blueprint(post_api.bp)
    app.register_blueprint(reply_api.bp)
    app.register_blueprint(comment_api.bp)

    return app