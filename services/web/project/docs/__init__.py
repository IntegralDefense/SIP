import os

from flask import Blueprint

this_dir = os.path.dirname(os.path.realpath(__file__))
static_folder = os.path.join(this_dir, '..', '..', 'docs', '_build', 'html')

bp = Blueprint('docs', __name__, url_prefix='/docs', static_url_path='/', static_folder=static_folder)

from project.docs import routes
