import os

basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    """ Base Configuration """

    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # Flask-Security
    SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT')
    SECURITY_CONFIRMABLE = False
    SECURITY_REGISTERABLE = False
    SECURITY_RECOVERABLE = False
    SECURITY_CHANGEABLE = True
    SECURITY_USER_IDENTITY_ATTRIBUTES = ['username']
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_SEND_PASSWORD_CHANGE_EMAIL = False
    SECURITY_SEND_PASSWORD_RESET_EMAIL = False
    SECURITY_SEND_PASSWORD_RESET_NOTICE_EMAIL = False

    """
    API PERMISSIONS
    
    The keys correspond to the HTTP method for the various API function calls.
    The values assigned to them represent the user role required to perform the call.
    Assigning the None role means that no roles or API keys are required to perform the call.
    
    NOTE: You can change these API roles to whatever you want, but do not delete or edit the
    admin role from the database. It is a required role to provide API functionality
    for creating and modifying user accounts and additional roles. 
    """

    # Create functions
    POST = 'analyst'

    # Read functions
    GET = None

    # Update functions
    PUT = 'analyst'

    # Delete functions
    DELETE = 'admin'


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_TEST_URL')


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
