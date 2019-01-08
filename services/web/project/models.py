import logging
import uuid
from abc import ABC

from project import db
from datetime import datetime
from flask import url_for
from flask_security import UserMixin, RoleMixin
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID

logger = logging.getLogger(__name__)


class GUID(TypeDecorator, ABC):
    """Platform-independent GUID type.

    Uses Postgresql's UUID type, otherwise uses
    CHAR(36), storing as stringified hex values.

    """
    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.uuid4())
            else:
                return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)


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
        page = int(args.get('page', 1))
        per_page = min(int(args.get('per_page', 10)), 100)

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

event_attack_vector_association = db.Table('event_attack_vector_mapping',
                                           db.Column('event_id', db.Integer, db.ForeignKey('event.id')),
                                           db.Column('event_attack_vector_id', db.Integer,
                                                     db.ForeignKey('event_attack_vector.id'))
                                           )

event_malware_association = db.Table('event_malware_mapping',
                                     db.Column('event_id', db.Integer, db.ForeignKey('event.id')),
                                     db.Column('malware_id', db.Integer, db.ForeignKey('malware.id'))
                                     )

event_prevention_tool_association = db.Table('event_prevention_tool_mapping',
                                             db.Column('event_id', db.Integer, db.ForeignKey('event.id')),
                                             db.Column('event_prevention_tool_id', db.Integer,
                                                       db.ForeignKey('event_prevention_tool.id'))
                                             )

event_reference_association = db.Table('event_reference_mapping',
                                       db.Column('event_id', db.Integer, db.ForeignKey('event.id')),
                                       db.Column('intel_reference_id', db.Integer, db.ForeignKey('intel_reference.id'))
                                       )

event_remediation_association = db.Table('event_remediation_mapping',
                                         db.Column('event_id', db.Integer, db.ForeignKey('event.id')),
                                         db.Column('event_remediation_id', db.Integer,
                                                   db.ForeignKey('event_remediation.id'))
                                         )

event_tag_association = db.Table('event_tag_mapping',
                                 db.Column('event_id', db.Integer, db.ForeignKey('event.id')),
                                 db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
                                 )

event_type_association = db.Table('event_type_mapping',
                                  db.Column('event_id', db.Integer, db.ForeignKey('event.id')),
                                  db.Column('event_type_id', db.Integer, db.ForeignKey('event_type.id'))
                                  )

indicator_campaign_association = db.Table('indicator_campaign_mapping',
                                          db.Column('campaign_id', db.Integer, db.ForeignKey('campaign.id')),
                                          db.Column('indicator_id', db.Integer, db.ForeignKey('indicator.id'))
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

malware_type_association = db.Table('malware_type_mapping',
                                    db.Column('malware_id', db.Integer, db.ForeignKey('malware.id')),
                                    db.Column('malware_type_id', db.Integer, db.ForeignKey('malware_type.id'))
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


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    active = db.Column(db.Boolean(), nullable=False, default=True)
    # apikey = db.Column(GUID(), unique=True, nullable=False, default=uuid.uuid4)
    apikey = db.Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    first_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    last_name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    roles = db.relationship('Role', secondary=roles_users_association, backref=db.backref('users', lazy='dynamic'))
    username = db.Column(db.String(255), nullable=False, unique=True)

    """
    events = db.relationship('Event',
                     secondary='join(IntelReference, Event, IntelReference.id == Event.intel_reference_id)',
                     primaryjoin='and_(User.id == IntelReference.user_id)',
                     order_by='Event.created_time', viewonly=True, backref='user'
                     )
    """

    def __str__(self):
        return str(self.username)


class Campaign(db.Model):
    __tablename__ = 'campaign'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    aliases = db.relationship('CampaignAlias', order_by='CampaignAlias.alias')
    created_time = db.Column(db.DateTime, default=datetime.utcnow)
    modified_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    name = db.Column(db.String(255), unique=True, nullable=False)

    def __str__(self):
        return str(self.name)


class CampaignAlias(db.Model):
    __tablename__ = 'campaign_alias'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    alias = db.Column(db.String(255), unique=True, nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)

    def __str__(self):
        return str(self.alias)


class Event(db.Model):
    __tablename__ = 'event'

    id = db.Column(db.Integer, primary_key=True, nullable=False)

    attack_vectors = db.relationship('EventAttackVector', secondary=event_attack_vector_association)
    campaign = db.relationship('Campaign')
    _campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=True)
    created_time = db.Column(db.DateTime, default=datetime.utcnow)
    disposition = db.relationship('EventDisposition')
    _disposition_id = db.Column(db.Integer, db.ForeignKey('event_disposition.id'), nullable=False)

    """
    indicators = db.relationship('Indicator',
                     secondary='join(IntelReference, EventReferenceMapping, IntelReference.id == EventReferenceMapping.intel_reference_id).'
                               'join(IndicatorReferenceMapping, IntelReference.id == IndicatorReferenceMapping.intel_reference_id).'
                               'join(Indicator, Indicator.id == IndicatorReferenceMapping.indicator_id)',
                     primaryjoin='and_(Event.id == EventReferenceMapping.event_id)',
                     order_by='Indicator.created_time', viewonly=True
                     )
    """

    malware = db.relationship('Malware', secondary=event_malware_association)
    name = db.Column(db.String(255), unique=True, nullable=False)
    prevention_tools = db.relationship('EventPreventionTool', secondary=event_prevention_tool_association)
    references = db.relationship('IntelReference', secondary=event_reference_association)
    remediations = db.relationship('EventRemediation', secondary=event_remediation_association)
    status = db.relationship('EventStatus')
    _status_id = db.Column(db.Integer, db.ForeignKey('event_status.id'), nullable=False)
    tags = db.relationship('Tag', secondary=event_tag_association)
    types = db.relationship('EventType', secondary=event_type_association)

    def __str__(self):
        return str(self.name)


class EventAttackVector(db.Model):
    __tablename__ = 'event_attack_vector'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    value = db.Column(db.String(255), unique=True, nullable=False)

    def __str__(self):
        return str(self.value)


class EventDisposition(db.Model):
    __tablename__ = 'event_disposition'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    value = db.Column(db.String(255), unique=True, nullable=False)

    def __str__(self):
        return str(self.value)


class EventPreventionTool(db.Model):
    __tablename__ = 'event_prevention_tool'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    value = db.Column(db.String(255), unique=True, nullable=False)

    def __str__(self):
        return str(self.value)


class EventRemediation(db.Model):
    __tablename__ = 'event_remediation'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    value = db.Column(db.String(255), unique=True, nullable=False)

    def __str__(self):
        return str(self.value)


class EventStatus(db.Model):
    __tablename__ = 'event_status'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    value = db.Column(db.String(255), unique=True, nullable=False)

    def __str__(self):
        return str(self.value)


class EventType(db.Model):
    __tablename__ = 'event_type'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    value = db.Column(db.String(255), unique=True, nullable=False)

    def __str__(self):
        return str(self.value)


class Indicator(PaginatedAPIMixin, db.Model):
    __tablename__ = 'indicator'
    __table_args__ = (
        db.UniqueConstraint('_type_id', 'value'),
    )

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    campaigns = db.relationship('Campaign', secondary=indicator_campaign_association)
    case_sensitive = db.Column(db.Boolean, default=False, nullable=False)
    confidence = db.relationship('IndicatorConfidence')
    _confidence_id = db.Column(db.Integer, db.ForeignKey('indicator_confidence.id'), nullable=False)
    created_time = db.Column(db.DateTime, default=datetime.utcnow)
    impact = db.relationship('IndicatorImpact')
    _impact_id = db.Column(db.Integer, db.ForeignKey('indicator_impact.id'), nullable=False)
    modified_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    references = db.relationship('IntelReference', secondary=indicator_reference_association)

    _children = db.relationship('Indicator', secondary=indicator_relationship_association,
                                primaryjoin=(indicator_relationship_association.c.parent_id == id),
                                secondaryjoin=(indicator_relationship_association.c.child_id == id),
                                backref=db.backref('_parent', lazy='select'), lazy='select')

    _equal = db.relationship('Indicator', secondary=indicator_equal_association,
                             primaryjoin=(indicator_equal_association.c.left_id == id),
                             secondaryjoin=(indicator_equal_association.c.right_id == id),
                             lazy='select')

    status = db.relationship('IndicatorStatus')
    _status_id = db.Column(db.Integer, db.ForeignKey('indicator_status.id'), nullable=False)
    substring = db.Column(db.Boolean, default=False, nullable=False)
    tags = db.relationship('Tag', secondary=indicator_tag_association)
    type = db.relationship('IndicatorType')
    _type_id = db.Column(db.Integer, db.ForeignKey('indicator_type.id'), nullable=False)
    value = db.Column(db.String(512), nullable=False)

    def __str__(self):
        return str('{} : {}'.format(self.type, self.value))

    def to_dict(self):
        children = self.get_children(grandchildren=False)
        children_all = self.get_children(grandchildren=True)

        equal = self.get_equal(recursive=False)
        equal_all = self.get_equal(recursive=True)

        data = {
            'id': self.id,
            'campaigns': [c.name for c in self.campaigns],
            'case_sensitive': bool(self.case_sensitive),
            'children': [i.id for i in children],
            'children_all': sorted([i.id for i in children_all]),
            'confidence': self.confidence.value,
            'created_time': self.created_time,
            'equal': [i.id for i in equal],
            'equal_all': sorted([i.id for i in equal_all]),
            'impact': self.impact.value,
            'modified_time': self.modified_time,
            'parent': self.get_parent().id if self.get_parent() else None,
            'references': [r.reference for r in self.references],
            'status': self.status.value,
            'substring': bool(self.substring),
            'tags': [t.value for t in self.tags],
            'type': self.type.value,
            'value': self.value
        }
        return data

    def add_child(self, other):
        if not self == other and not other._parent:
            self._children.append(other)
            return True
        return False

    def remove_child(self, other):
        result = False
        try:
            self._children.remove(other)
            result = True
        except ValueError:
            pass
        try:
            other._parent.remove(self)
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
            return self._parent[0]
        except IndexError:
            return None

    def get_children(self, grandchildren=True, _orig=None, _results=None):
        if not grandchildren:
            return self._children

        if _orig is None:
            _orig = self
            _results = []

        for ind in self._children:
            if ind not in _results:
                _results.append(ind)
                _results = ind.get_children(_orig=_orig, _results=_results)

        return _results

    def is_equal(self, other, recursive=True):
        if not recursive:
            if other in self._equal or self in other._equal:
                return True
            return False
        return other in self.get_equal(recursive=True)

    def make_equal(self, other):
        if not self == other and not self.is_equal(other, recursive=True):
            self._equal.append(other)
            other._equal.append(self)
            return True
        return False

    def remove_equal(self, other):
        result = False
        try:
            self._equal.remove(other)
            result = True
        except ValueError:
            pass
        try:
            other._equal.remove(self)
            result = True
        except ValueError:
            pass
        return result

    def get_equal(self, recursive=True, _orig=None, _already_checked=None, _results=None):
        if _already_checked is None:
            _already_checked = []
        if not recursive:
            return self._equal

        if _orig is None:
            _orig = self
            _already_checked = []
            _results = []

        for ind in self._equal:
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


class IndicatorImpact(db.Model):
    __tablename__ = 'indicator_impact'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    value = db.Column(db.String(255), unique=True, nullable=False)

    def __str__(self):
        return str(self.value)


class IndicatorStatus(db.Model):
    __tablename__ = 'indicator_status'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    value = db.Column(db.String(255), unique=True, nullable=False)

    def __str__(self):
        return str(self.value)


class IndicatorType(db.Model):
    __tablename__ = 'indicator_type'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    value = db.Column(db.String(255), unique=True, nullable=False)

    def __str__(self):
        return str(self.value)


class IntelSource(db.Model):
    __tablename__ = 'intel_source'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    value = db.Column(db.String(255), unique=True, nullable=False)

    def __str__(self):
        return str(self.value)


class IntelReference(db.Model):
    __tablename__ = 'intel_reference'
    __table_args__ = (
        db.UniqueConstraint('_intel_source_id', 'reference'),
    )

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user = db.relationship('User')
    _user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    intel_source = db.relationship('IntelSource')
    _intel_source_id = db.Column(db.Integer, db.ForeignKey('intel_source.id'), nullable=False)
    reference = db.Column(db.String(512), index=True, nullable=False)

    def __str__(self):
        return str('{} : {}'.format(self.intel_source, self.reference))


class Malware(db.Model):
    __tablename__ = 'malware'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(255), unique=True, nullable=False)
    types = db.relationship('MalwareType', secondary=malware_type_association)

    def __str__(self):
        return str(self.name)


class MalwareType(db.Model):
    __tablename__ = 'malware_type'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    value = db.Column(db.String(255), unique=True, nullable=False)

    def __str__(self):
        return str(self.value)


class Tag(db.Model):
    __tablename__ = 'tag'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    value = db.Column(db.String(255), unique=True, nullable=False)

    def __str__(self):
        return str(self.value)
