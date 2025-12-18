import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = "super-secret-key"
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@localhost/medicapp"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, "..", "uploads")
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf"}