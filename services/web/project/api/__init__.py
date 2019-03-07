from flask import Blueprint

bp = Blueprint('api', __name__, url_prefix='/api')

from project.api.routes import campaign
from project.api.routes import campaign_alias

from project.api.routes import indicator
from project.api.routes import indicator_confidence
from project.api.routes import indicator_equal
from project.api.routes import indicator_impact
from project.api.routes import indicator_relationship
from project.api.routes import indicator_status
from project.api.routes import indicator_type

from project.api.routes import intel_reference
from project.api.routes import intel_source

from project.api.routes import role

from project.api.routes import tag

from project.api.routes import user
