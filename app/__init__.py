from flask import Flask
from .config import Config
from .extensions import db, migrate, cache, login_manager, jwt, mail
from .routes import register_blueprints


def create_app():
    app = Flask(
        __name__,
        static_folder="static",
        static_url_path="/static"
    )
    app.config.from_object(Config)
    mail.init_app(app)

    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = "warning"
    
    jwt.init_app(app)
    cache.init_app(app)

    register_blueprints(app)

    return app
