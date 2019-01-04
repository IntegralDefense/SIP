import logging
from logging.handlers import TimedRotatingFileHandler
import os

from flask import Flask, jsonify, url_for
from flask_admin import Admin, AdminIndexView
from flask_admin import helpers as admin_helpers
from flask_migrate import Migrate
from flask_security import Security, SQLAlchemyUserDatastore, current_user
from flask_sqlalchemy import SQLAlchemy

from project.forms import ExtendedLoginForm

admin = Admin(name='Intelooper', url='/intelooper')
db = SQLAlchemy()
migrate = Migrate()
security = Security()

def create_app(script_info=None):

    # Create the app
    app = Flask(__name__)

    # Set up the config
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

    # Start logging
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = TimedRotatingFileHandler('logs/intelooper.log',  when='midnight', interval=1, backupCount=6)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(filename)s:%(lineno)d - %(message)s'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Intelooper starting')

    # Flask-SQLAlchemy
    db.init_app(app)

    # Flask-Migrate
    migrate.init_app(app, db)

    # Flask-Security
    user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
    security_ctx = security.init_app(app, datastore=user_datastore, login_form=ExtendedLoginForm)

    # Flask-Admin
    admin.init_app(app)

    # GUI/Admin Blueprint
    from project.gui import bp as gui_bp
    app.register_blueprint(gui_bp)

    # API Blueprint
    from project.api import bp as api_bp
    app.register_blueprint(api_bp)

    # Inject Flask-Security into Flask-Admin so things like current_user and roles
    # work inside the custom view models.
    @security_ctx.context_processor
    def security_context_processor():
        return dict(
            admin_base_template=admin.base_template,
            admin_view=admin.index_view,
            h=admin_helpers,
            get_url=url_for
            )

    @app.shell_context_processor
    def ctx():
        return {'app': app, 'db': db}

    return app

from project import models
