from flask import Blueprint

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")
from .dashboard import *
from .doctors import *
from .patients import *
from .reports import *
