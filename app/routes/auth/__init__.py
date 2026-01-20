from flask import Blueprint

auth_bp = Blueprint("auth", __name__)
from .login import *
from .register import *
from .logout import *
