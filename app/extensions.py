from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache
from flask_login import LoginManager
from flask_jwt_extended import JWTManager

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

cache = Cache(config={
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 28800 # 8 hours
})
