from flask import Blueprint

bp = Blueprint('api', __name__, url_prefix='/api')

from project.api.routes import event_attack_vector
from project.api.routes import event_disposition
from project.api.routes import event_prevention_tool
from project.api.routes import event_remediation
from project.api.routes import event_status
from project.api.routes import event_type

from project.api.routes import indicator
from project.api.routes import indicator_confidence
from project.api.routes import indicator_equal
from project.api.routes import indicator_impact
from project.api.routes import indicator_relationship
from project.api.routes import indicator_status
from project.api.routes import indicator_type
