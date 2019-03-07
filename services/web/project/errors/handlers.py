from flask import request

from project import db
from project.errors import bp
from project.api.errors import error_response
from project.gui.views import DefaultView


@bp.app_errorhandler(404)
def not_found_error(error):
    if request.path.startswith('/api/'):
        return error_response(404, 'API endpoint not found')
    else:
        return DefaultView().render('errors/404.html'), 404


@bp.app_errorhandler(500)
def internal_error(error):
    if request.path.startswith('/api/'):
        db.session.rollback()
        return error_response(500, 'Internal server error')
    else:

        return DefaultView().render('errors/500.html'), 500
