from flask import Blueprint

bp = Blueprint('errors', __name__)

from project.errors import handlers
