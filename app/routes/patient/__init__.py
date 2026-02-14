from flask import Blueprint

patient_bp = Blueprint("patient", __name__, url_prefix="/patient")
from .dashboard import *
from .profile import *
from .appointments import *
from .booking import *
from .availableDoctors import *
from .visibility import *
from .verification import *
# from .medical_records import *
# from .prescriptions import *