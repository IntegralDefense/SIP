from flask import redirect, url_for

from project.gui import bp


@bp.route('/')
@bp.route('/index')
def index():
    return redirect(url_for('admin.index'))
