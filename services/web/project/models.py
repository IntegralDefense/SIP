import logging
import uuid

from project import db
from datetime import datetime
from flask import url_for
from flask_security import UserMixin, RoleMixin
logger = logging.getLogger(__name__)


def generate_apikey():
    return str(uuid.uuid4())


"""
PAGINATED API QUERY MIXIN
"""


class PaginatedAPIMixin:
    @staticmethod
    def to_collection_dict(query, endpoint, **kwargs):
        """ Returns a paginated dictionary of a query. """

        # Create a copy of the request arguments so that we can modify them.
        args = kwargs.copy()

        # Read the page and per_page values or use the defaults.
        if 'page' in args:
            page = int(args['page'][0])
        else:
            page = 1
        if 'per_page' in args:
            per_page = min(int(args['per_page'][0]), 100)
        else:
            per_page = 10

        # Now that we have the page and per_page values, remove them
        # from the arguments so that the url_for function does not
        # receive duplicates of them.
        try:
            del args['page']
        except KeyError:
            pass
        try:
            del args['per_page']
        except KeyError:
            pass

        # Paginate the query.
        resources = query.paginate(page, per_page, False)

        # Generate the response dictionary.
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page, **args),
                'next': url_for(endpoint, page=page + 1, per_page=per_page, **args) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page, **args) if resources.has_prev else None
            }
        }
        return data


"""
ASSOCIATION TABLES
"""


indicator_campaign_association = db.Table('indicator_campaign_mapping',
                                          db.Column('indicator_id', db.Integer, db.ForeignKey('indicator.id')),
                                          db.Column('campaign_id', db.Integer, db.ForeignKey('campaign.id'))
                                          )

indicator_equal_association = db.Table('indicator_equal_mapping',
                                       db.Column('left_id', db.Integer, db.ForeignKey('indicator.id'),
                                                 primary_key=True),
                                       db.Column('right_id', db.Integer, db.ForeignKey('indicator.id'),
                                                 primary_key=True)
                                       )

indicator_reference_association = db.Table('indicator_reference_mapping',
                                           db.Column('indicator_id', db.Integer, db.ForeignKey('indicator.id')),
                                           db.Column('intel_reference_id', db.Integer,
                                                     db.ForeignKey('intel_reference.id'))
                                           )

indicator_relationship_association = db.Table('indicator_relationship_mapping',
                                              db.Column('parent_id', db.Integer, db.ForeignKey('indicator.id'),
                                                        primary_key=True),
                                              db.Column('child_id', db.Integer, db.ForeignKey('indicator.id'),
                                                        primary_key=True)
                                              )

indicator_tag_association = db.Table('indicator_tag_mapping',
                                     db.Column('indicator_id', db.Integer, db.ForeignKey('indicator.id')),
                                     db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
                                     )

roles_users_association = db.Table('role_user_mapping',
                                   db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                                   db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

"""
TABLE CLASS DEFINITIONS
"""


class Role(db.Model, RoleMixin):
    __tablename__ = 'role'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return str(self.name)

    def to_dict(self):
        return {'id': self.id, 'description': self.description, 'name': self.name}


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    active = db.Column(db.Boolean(), nullable=False, default=True)
    apikey = db.Column(db.String(36), index=True, unique=True, nullable=False, default=generate_apikey)
    email = db.Column(db.String(255), nullable=False, unique=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(130), nullable=False)
    roles = db.relationship('Role', secondary=roles_users_association, backref=db.backref('users', lazy='dynamic'))
    username = db.Column(db.String(255), nullable=False, unique=True)

    def __str__(self):
        return str(self.username)

    def to_dict(self):
        return {'id': self.id,
                'active': self.active,
                'email': self.email,
                'first_name': self.first_name,
                'last_name': self.last_name,
                'roles': sorted([r.name for r in self.roles]),
                'username': self.username}


class Campaign(db.Model):
    __tablename__ = 'campaign'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    aliases = db.relationship('CampaignAlias', order_by='CampaignAlias.alias')
    created_time = db.Column(db.DateTime, default=datetime.utcnow)
    modified_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    name = db.Column(db.String(255), unique=True, nullable=False)

    def __str__(self):
        return str(self.name)

    def to_dict(self):
        return {'id': self.id,
                'aliases': sorted([a.alias for a in self.aliases]),
                'created_time': self.created_time,
                'modified_time': self.modified_time,
                'name': self.name}


class CampaignAlias(db.Model):
    __tablename__ = 'campaign_alias'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    alias = db.Column(db.String(255), unique=True, nullable=False)
    campaign = db.relationship('Campaign')
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)

    def __str__(self):
        return str(self.alias)

    def to_dict(self):
        return {'id': self.id,
                'alias': self.alias,
                'campaign': self.campaign.name}


class Indicator(PaginatedAPIMixin, db.Model):
    __tablename__ = 'indicator'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    campaigns = db.relationship('Campaign', secondary=indicator_campaign_association)
    case_sensitive = db.Column(db.Boolean, default=False, nullable=False)
    confidence = db.relationship('IndicatorConfidence')
    confidence_id = db.Column(db.Integer, db.ForeignKey('indicator_confidence.id'), nullable=False)
    created_time = db.Column(db.DateTime, default=datetime.utcnow)
    impact = db.relationship('IndicatorImpact')
    impact_id = db.Column(db.Integer, db.ForeignKey('indicator_impact.id'), nullable=False)
    modified_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    references = db.relationship('IntelReference', secondary=indicator_reference_association)

    children = db.relationship('Indicator', secondary=indicator_relationship_association,
                               primaryjoin=(indicator_relationship_association.c.parent_id == id),
                               secondaryjoin=(indicator_relationship_association.c.child_id == id),
                               backref=db.backref('parent', lazy='select'), lazy='select')

    equal = db.relationship('Indicator', secondary=indicator_equal_association,
                            primaryjoin=(indicator_equal_association.c.left_id == id),
                            secondaryjoin=(indicator_equal_association.c.right_id == id),
                            lazy='select')

    status = db.relationship('IndicatorStatus')
    status_id = db.Column(db.Integer, db.ForeignKey('indicator_status.id'), nullable=False)
    substring = db.Column(db.Boolean, default=False, nullable=False)
    tags = db.relationship('Tag', secondary=indicator_tag_association)
    type = db.relationship('IndicatorType')
    type_id = db.Column(db.Integer, db.ForeignKey('indicator_type.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User')
    value = db.Column(db.UnicodeText, nullable=False)

    def __str__(self):
        return str('{} : {}'.format(self.type, self.value))

    def to_dict(self):
        children = self.get_children(grandchildren=False)
        all_children = self.get_children(grandchildren=True)

        equal = self.get_equal(recursive=False)
        all_equal = self.get_equal(recursive=True)

        data = {
            'id': self.id,
            'all_children': sorted([i.id for i in all_children]),
            'all_equal': sorted([i.id for i in all_equal]),
            'campaigns': [c.to_dict() for c in self.campaigns],
            'case_sensitive': bool(self.case_sensitive),
            'children': sorted([i.id for i in children]),
            'confidence': self.confidence.value,
            'created_time': self.created_time,
            'equal': sorted([i.id for i in equal]),
            'impact': self.impact.value,
            'modified_time': self.modified_time,
            'parent': self.get_parent().id if self.get_parent() else None,
            'references': [r.to_dict() for r in self.references],
            'status': self.status.value,
            'substring': bool(self.substring),
            'tags': sorted([t.value for t in self.tags]),
            'type': self.type.value,
            'user': self.user.username,
            'value': self.value
        }
        return data

    def add_child(self, other):
        if not self == other and not other.parent:
            self.children.append(other)
            return True
        return False

    def remove_child(self, other):
        result = False
        try:
            self.children.remove(other)
            result = True
        except ValueError:
            pass
        try:
            other.parent.remove(self)
            result = True
        except ValueError:
            pass
        return result

    def is_parent(self, other, grandchildren=True):
        return other in self.get_children(grandchildren=grandchildren)

    def is_child(self, other, grandchildren=True):
        return self in other.get_children(grandchildren=grandchildren)

    def get_parent(self):
        try:
            return self.parent[0]
        except IndexError:
            return None

    def get_children(self, grandchildren=True, _orig=None, _results=None):
        if not grandchildren:
            return self.children

        if _orig is None:
            _orig = self
            _results = []

        for ind in self.children:
            if ind not in _results:
                _results.append(ind)
                _results = ind.get_children(_orig=_orig, _results=_results)

        return _results

    def is_equal(self, other, recursive=True):
        if not recursive:
            if other in self.equal or self in other.equal:
                return True
            return False
        return other in self.get_equal(recursive=True)

    def make_equal(self, other):
        if not self == other and not self.is_equal(other, recursive=True):
            self.equal.append(other)
            other.equal.append(self)
            return True
        return False

    def remove_equal(self, other):
        result = False
        try:
            self.equal.remove(other)
            result = True
        except ValueError:
            pass
        try:
            other.equal.remove(self)
            result = True
        except ValueError:
            pass
        return result

    def get_equal(self, recursive=True, _orig=None, _already_checked=None, _results=None):
        if _already_checked is None:
            _already_checked = []
        if not recursive:
            return self.equal

        if _orig is None:
            _orig = self
            _already_checked = []
            _results = []

        for ind in self.equal:
            if ind == _orig:
                continue
            if ind not in _results:
                _results.append(ind)
            if ind not in _already_checked:
                _already_checked.append(ind)
                _results = ind.get_equal(_orig=_orig, _already_checked=_already_checked, _results=_results)

        try:
            _results.remove(_orig)
        except ValueError:
            pass

        return _results


class IndicatorConfidence(db.Model):
    __tablename__ = 'indicator_confidence'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    value = db.Column(db.String(255), unique=True, nullable=False)

    def __str__(self):
        return str(self.value)

    def to_dict(self):
        return {'id': self.id,
                'value': self.value}


class IndicatorImpact(db.Model):
    __tablename__ = 'indicator_impact'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    value = db.Column(db.String(255), unique=True, nullable=False)

    def __str__(self):
        return str(self.value)

    def to_dict(self):
        return {'id': self.id,
                'value': self.value}


class IndicatorStatus(db.Model):
    __tablename__ = 'indicator_status'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    value = db.Column(db.String(255), unique=True, nullable=False)

    def __str__(self):
        return str(self.value)

    def to_dict(self):
        return {'id': self.id,
                'value': self.value}


class IndicatorType(db.Model):
    __tablename__ = 'indicator_type'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    value = db.Column(db.String(255), unique=True, nullable=False)

    def __str__(self):
        return str(self.value)

    def to_dict(self):
        return {'id': self.id,
                'value': self.value}


class IntelReference(PaginatedAPIMixin, db.Model):
    __tablename__ = 'intel_reference'
    __table_args__ = (
        db.UniqueConstraint('intel_source_id', 'reference'),
    )

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user = db.relationship('User')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reference = db.Column(db.String(512), index=True, nullable=False)
    source = db.relationship('IntelSource')
    intel_source_id = db.Column(db.Integer, db.ForeignKey('intel_source.id'), nullable=False)

    """
    viewonly is set to True on this relationship so that if any indicator exists that uses this
    reference, the reference cannot be deleted due to a foreign key constraint.
    """
    indicators = db.relationship('Indicator', secondary=indicator_reference_association, viewonly=True, lazy='dynamic')

    def __str__(self):
        return str('{} : {}'.format(self.source, self.reference))

    def to_dict(self):
        return {'id': self.id,
                'reference': self.reference,
                'source': self.source.value,
                'user': self.user.username}


class IntelSource(db.Model):
    __tablename__ = 'intel_source'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    value = db.Column(db.String(255), unique=True, nullable=False)

    def __str__(self):
        return str(self.value)

    def to_dict(self):
        return {'id': self.id,
                'value': self.value}


class Tag(db.Model):
    __tablename__ = 'tag'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    value = db.Column(db.String(255), nullable=False)

    def __str__(self):
        return str(self.value)

    def to_dict(self):
        return {'id': self.id,
                'value': self.value}
