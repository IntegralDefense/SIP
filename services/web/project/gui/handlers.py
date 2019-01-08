from project import db
from project.gui import bp
from project.gui.views import DefaultView


@bp.app_errorhandler(404)
def not_found_error():
    return DefaultView().render('errors/404.html'), 404


@bp.app_errorhandler(500)
def internal_error():
    db.session.rollback()
    return DefaultView().render('errors/500.html'), 500
