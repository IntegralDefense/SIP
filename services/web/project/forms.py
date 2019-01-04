from flask_wtf import FlaskForm
from flask_security.forms import LoginForm
from flask_security.utils import encrypt_password
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo

# Flask-Security wants you to log in with email address. This 'hack' changes the login form to display Username instead.
class ExtendedLoginForm(LoginForm):
    email = StringField('Username', [DataRequired()])
