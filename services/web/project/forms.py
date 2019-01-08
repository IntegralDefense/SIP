from flask_security.forms import LoginForm
from wtforms import StringField
from wtforms.validators import DataRequired


# Flask-Security wants you to log in with email address. This 'hack' changes the login form to display Username instead.
class ExtendedLoginForm(LoginForm):
    email = StringField('Username', [DataRequired()])
