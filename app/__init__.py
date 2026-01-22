from flask import Flask
from .config import Config
from .extensions import db, migrate
from .routes import register_blueprints

def create_app():
    app = Flask(
        __name__,
        static_folder="static",
        static_url_path="/static"
    )
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    register_blueprints(app)

    with app.app_context():
        db.create_all()

    return app
