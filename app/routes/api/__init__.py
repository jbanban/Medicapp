from flask import Blueprint

api_bp = Blueprint("api", __name__, url_prefix="/api")
from .appointments import *
from .availability import *
from .schedules import *
from .medical_visibility import *
