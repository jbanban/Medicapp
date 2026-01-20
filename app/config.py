class Config:
    SECRET_KEY = "superSecretHiddenAuthenticatedKey"
    SQLALCHEMY_DATABASE_URI = "sqlite:///medicapp.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = "app/static/uploads"