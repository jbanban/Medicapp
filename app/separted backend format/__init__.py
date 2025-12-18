from flask import Flask
from .config import Config
from .extensions import db, migrate, login_manager
from .routes import register_blueprints

def create_app(config_object=Config):
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(config_object)

    # extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    from .models.account import Account

    @login_manager.user_loader
    def load_user(user_id):
        return Account.query.get(int(user_id))

    # blueprints
    register_blueprints(app)

    return app
