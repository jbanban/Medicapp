import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "superSecretHiddenAuthenticatedKey")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "superSecretHiddenjwtSecureSecret_Key")
    
    SQLALCHEMY_DATABASE_URI = "sqlite:///medicapp.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    UPLOAD_FOLDER = "app/static/uploads"

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = timedelta(days=7)