from flask import Blueprint

from project import admin, db, models
from project.gui.views import AdminView, AdminUserView, AnalystView, CampaignView, IndicatorView, LoginMenuLink, \
    LogoutMenuLink

bp = Blueprint('gui', __name__)

admin.add_view(CampaignView(models.Campaign, db.session, category='Campaigns'))
admin.add_view(AnalystView(models.CampaignAlias, db.session, category='Campaigns'))

admin.add_view(IndicatorView(models.Indicator, db.session, category='Indicators'))
admin.add_view(AnalystView(models.IndicatorConfidence, db.session, category='Indicators'))
admin.add_view(AnalystView(models.IndicatorImpact, db.session, category='Indicators'))
admin.add_view(AnalystView(models.IndicatorStatus, db.session, category='Indicators'))
admin.add_view(AnalystView(models.IndicatorType, db.session, category='Indicators'))

admin.add_view(AnalystView(models.IntelReference, db.session, category='Intel'))
admin.add_view(AnalystView(models.IntelSource, db.session, category='Intel'))

admin.add_view(AnalystView(models.Tag, db.session))

admin.add_view(AdminView(models.Role, db.session, category='Admin'))
admin.add_view(AdminUserView(models.User, db.session, category='Admin'))

admin.add_link(LoginMenuLink(name='Login', url='/login'))
admin.add_link(LogoutMenuLink(name='Logout', url='/logout'))

from project.gui import routes
