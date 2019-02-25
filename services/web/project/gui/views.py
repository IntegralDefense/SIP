from flask import redirect, url_for
from flask_admin import Admin, AdminIndexView
from flask_admin.base import BaseView
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import SecureForm
from flask_admin.menu import MenuLink
from flask_security import current_user
from flask_security.utils import hash_password
from wtforms import PasswordField, validators

from project.config import BaseConfig


# Restrict access to 'admin' users
class AdminView(ModelView):
    form_base_class = SecureForm

    def is_accessible(self):
        return current_user.has_role('admin')

    def inaccessible_callback(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('index'))


# Restrict access to 'analyst' users
class AnalystView(ModelView):
    form_base_class = SecureForm

    def is_accessible(self):
        return current_user.has_role('analyst')

    def inaccessible_callback(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('index'))


# Restrict access to logged in users.
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated


# Only show the Login link if user is logged out.
class LoginMenuLink(MenuLink):
    def is_accessible(self):
        return not current_user.is_authenticated


# Only show the Logout link if the user is logged in.
class LogoutMenuLink(MenuLink):
    def is_accessible(self):
        return current_user.is_authenticated


class CampaignView(AnalystView):
    form_excluded_columns = ('created_time', 'modified_time')


class IndicatorView(AnalystView):
    column_exclude_list = ('children', 'parent', 'equal',)
    form_excluded_columns = ('children', 'parent', 'equal', 'created_time', 'modified_time',)


# Enable editing of Users but replace the 'password' field with a separate one that gets hashed upon submit.
class AdminUserView(AdminView):

    # Do not allow deleting of users... set to inactive instead.
    can_delete = False

    # Don't display the password on the list of Users
    column_exclude_list = ('password',)

    # Don't include the standard password field when creating or editing a User (but see below)
    form_excluded_columns = ('password',)

    # Automatically display human-readable names for the current and available Roles when creating or editing a User
    column_auto_select_related = True

    # On the form for creating or editing a User, don't display a field corresponding to the model's password field.
    # There are two reasons for this. First, we want to encrypt the password before storing in the database. Second,
    # we want to use a password field (with the input masked) rather than a regular text field.
    def scaffold_form(self):

        # Start with the standard form as provided by Flask-Admin. We've already told Flask-Admin to exclude the
        # password field from this form.
        form_class = super(AdminUserView, self).scaffold_form()

        # Add a password field, naming it "password2" and labeling it "New Password".
        form_class.password2 = PasswordField('New Password', [validators.Length(min=BaseConfig.MINIMUM_PASSWORD_LENGTH)])
        return form_class

    # This callback executes when the user saves changes to a newly-created or edited User -- before the changes are
    # committed to the database.
    def on_model_change(self, form, model, is_created):
        model.password = hash_password(model.password2)


# Basic view that everyone can see
class DefaultView(BaseView):

    def __init__(self, *args, **kwargs):
        self._default_view = True
        super(DefaultView, self).__init__(*args, **kwargs)
        self.admin = Admin(name='SIP', url='/SIP')
        self.admin.add_link(LoginMenuLink(name='Login', url='/login'))
        self.admin.add_link(LogoutMenuLink(name='Logout', url='/logout'))
