from flask import Blueprint

doctor_bp = Blueprint("doctor", __name__, url_prefix="/doctor")
from .dashboard import *
from .appointments import *
from .schedule import *
from .profile import *
from .patients import *
from .secretary import *
# from .medical_records import *
# from .prescriptions import *