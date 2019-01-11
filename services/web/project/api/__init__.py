from flask import Blueprint

bp = Blueprint('api', __name__, url_prefix='/api')

from project.api.routes import indicator
from project.api.routes import indicator_confidence
from project.api.routes import indicator_equal
from project.api.routes import indicator_relationship
