from flask import Blueprint

bp = Blueprint('api', __name__, url_prefix='/api')

from project.api.routes import indicator
