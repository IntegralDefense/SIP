from flask import jsonify, request, url_for

from project import db
from project.api import bp
from project.api.decorators import api_admin, api_analyst
from project.api.errors import error_response
from project.api.helpers import parse_boolean
from project.models import Indicator, IndicatorConfidence, IndicatorImpact, IndicatorStatus, IndicatorType, Tag

"""
CREATE
"""

@bp.route('/indicator', methods=['POST'])
@api_analyst
def create_indicator():
    """ Creates a new indicator. """

    data = request.values or {}

    # Verify the required fields (type and value) are present.
    if not 'type' in data or not 'value' in data:
        return error_response(400, 'Request must include "type" and "value"')

    # Verify the case-sensitive value (defaults to False).
    if 'case_sensitive' in data:
        case_sensitive = parse_boolean(data['case_sensitive'])
    else:
        case_sensitive = False

    # Verify the confidence (has default).
    if not 'confidence' in data:
        confidence = IndicatorConfidence.query.order_by(IndicatorConfidence.id).limit(1).first()
    else:
        confidence = IndicatorConfidence.query.filter_by(value=data['confidence']).first()
        if not confidence:
            results = IndicatorConfidence.query.all()
            acceptable = sorted([r.value for r in results])
            return error_response(400, 'confidence must be one of: {}'.format(', '.join(acceptable)))

    # Verify the impact (has default).
    if not 'impact' in data:
        impact = IndicatorImpact.query.order_by(IndicatorImpact.id).limit(1).first()
    else:
        impact = IndicatorImpact.query.filter_by(value=data['impact']).first()
        if not impact:
            results = IndicatorImpact.query.all()
            acceptable = sorted([r.value for r in results])
            return error_response(400, 'impact must be one of: {}'.format(', '.join(acceptable)))

    # Verify the status (has default).
    if not 'status' in data:
        status = IndicatorStatus.query.order_by(IndicatorStatus.id).limit(1).first()
    else:
        status = IndicatorStatus.query.filter_by(value=data['status']).first()
        if not status:
            results = IndicatorStatus.query.all()
            acceptable = sorted([r.value for r in results])
            return error_response(400, 'status must be one of: {}'.format(', '.join(acceptable)))

    # Verify the substring value (defaults to False).
    if 'substring' in data:
        substring = parse_boolean(data['substring'])
    else:
        substring = False

    # Verify the type.
    _type = IndicatorType.query.filter_by(value=data['type']).first()
    if not _type:
        results = IndicatorType.query.all()
        acceptable = sorted([r.value for r in results])
        return error_response(400, 'type must be one of: {}'.format(', '.join(acceptable)))

    # Verify this type+value does not already exist.
    existing = Indicator.query.filter_by(_type_id=_type.id, value=data['value']).first()
    if existing:
        return error_response(409, 'Indicator already exists: {}'.format(existing.id), url_for('api.get_indicator_by_id', id=existing.id))

    indicator = Indicator(case_sensitive=case_sensitive, _confidence_id=confidence.id, _impact_id=impact.id, _status_id=status.id, substring=substring, _type_id=_type.id, value=data['value'])

    db.session.add(indicator)
    db.session.commit()

    response = jsonify(indicator.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_indicator_by_id', id=indicator.id)
    return response

@bp.route('/indicator/relationship/<int:parent_id>/<int:child_id>', methods=['POST'])
@api_analyst
def create_relationship(parent_id, child_id):
    """ Creates a parent/child relationship between two indicators """

    data = request.values or {}

    parent_indicator = Indicator.query.get(parent_id)
    if not parent_indicator:
        return error_response(404, 'parent indicator not found')

    child_indicator = Indicator.query.get(child_id)
    if not child_indicator:
        return error_response(404, 'child indicator not found')

    if parent_id == child_id:
        return error_response(400, 'cannot add indicator to its own children')

    result = parent_indicator.add_child(child_indicator)
    if result:
        db.session.commit()
        return '', 204
    else:
        return error_response(400, 'the child indicator already has a parent')

@bp.route('/indicator/equal/<int:id1>/<int:id2>', methods=['POST'])
@api_analyst
def create_equal(id1, id2):
    """ Creates an equal to relationship between two indicators """

    data = request.values or {}

    indicator1 = Indicator.query.get(id1)
    if not indicator1:
        return error_response(404, 'a indicator not found')

    indicator2 = Indicator.query.get(id2)
    if not indicator2:
        return error_response(404, 'b indicator not found')

    if id1 == id2:
        return error_response(400, 'cannot make indicator equal to itself')

    result = indicator1.make_equal(indicator2)
    if result:
        db.session.commit()
        return '', 204
    else:
        return error_response(400, 'the indicators are already equal')

"""
READ
"""

@bp.route('/indicator/<int:id>', methods=['GET'])
def get_indicator_by_id(id):
    """ Gets a single indicator given its ID. """

    indicator = Indicator.query.get(id)
    if not indicator:
        return error_response(404, 'Indicator ID not found: {}'.format(id))

    return jsonify(indicator.to_dict())

@bp.route('/indicators', methods=['GET'])
def search_indicators():
    """ Gets a paginated list of indicators based on various filter criteria. """

    filters = set()

    # Case-sensitive filter
    if 'case_sensitive' in request.args:
        arg = parse_boolean(request.args.get('case_sensitive'), default=None)
        filters.add(Indicator.case_sensitive.is_(arg))

    # Confidence filter
    if 'confidence' in request.args:
        confidence = IndicatorConfidence.query.filter_by(value=request.args.get('confidence')).first()
        if confidence:
            id = confidence.id
        else:
            id = -1
        filters.add(Indicator._confidence_id == id)

    # Impact filter
    if 'impact' in request.args:
        impact = IndicatorImpact.query.filter_by(value=request.args.get('impact')).first()
        if impact:
            id = impact.id
        else:
            id = -1
        filters.add(Indicator._impact_id == id)

    # Status filter
    if 'status' in request.args:
        status = IndicatorStatus.query.filter_by(value=request.args.get('status')).first()
        if status:
            id = status.id
        else:
            id = -1
        filters.add(Indicator._status_id == id)

    # Substring filter
    if 'substring' in request.args:
        arg = parse_boolean(request.args.get('substring'), default=None)
        filters.add(Indicator.substring.is_(arg))

    # Tags filter
    if 'tags' in request.args:
        search_tags = request.args.get('tags').split(',')
        for search_tag in search_tags:
            filters.add(Indicator.tags.any(value=search_tag))

    # Type filter
    if 'type' in request.args:
        _type = IndicatorType.query.filter_by(value=request.args.get('type')).first()
        if _type:
            id = _type.id
        else:
            id = -1
        filters.add(Indicator._type_id == id)

    # Value filter
    if 'value' in request.args:
        filters.add(Indicator.value.like('%{}%'.format(request.args.get('value'))))

    data = Indicator.to_collection_dict(Indicator.query.filter(*filters), 'api.search_indicators', **request.args)
    return jsonify(data)

"""
UPDATE
"""

@bp.route('/indicator/<int:id>', methods=['PUT'])
@api_analyst
def update_indicator(id):
    """ Updates an existing indicator. """

    indicator = Indicator.query.get(id)
    if not indicator:
        return error_response(404, 'Indicator ID not found: {}'.format(id))

    data = request.values or {}

    # Verify the confidence.
    if 'confidence' in data:
        confidence = IndicatorConfidence.query.filter_by(value=data['confidence']).first()
        if not confidence:
            results = IndicatorConfidence.query.all()
            acceptable = sorted([r.value for r in results])
            return error_response(400, 'confidence must be one of: {}'.format(', '.join(acceptable)))
        indicator.confidence = confidence

    # Verify the imapct.
    if 'impact' in data:
        impact = IndicatorImpact.query.filter_by(value=data['impact']).first()
        if not impact:
            results = IndicatorImpact.query.all()
            acceptable = sorted([r.value for r in results])
            return error_response(400, 'impact must be one of: {}'.format(', '.join(acceptable)))
        indicator.impact = impact

    # Verify the status.
    if 'status' in data:
        status = IndicatorStatus.query.filter_by(value=data['status']).first()
        if not status:
            results = IndicatorStatus.query.all()
            acceptable = sorted([r.value for r in results])
            return error_response(400, 'status must be one of: {}'.format(', '.join(acceptable)))
        indicator.status = status

    db.session.commit()

    response = jsonify(indicator.to_dict())
    return response

"""
DELETE
"""

@bp.route('/indicator/<int:id>', methods=['DELETE'])
@api_admin
def delete_indicator(id):
    """ Deletes an indicator """

    indicator = Indicator.query.get(id)
    if not indicator:
        return error_response(404, 'Indicator ID not found: {}'.format(id))

    db.session.delete(indicator)
    db.session.commit()

    return '', 204

@bp.route('/indicator/relationship/<int:parent_id>/<int:child_id>', methods=['DELETE'])
@api_analyst
def delete_relationship(parent_id, child_id):
    """ Deletes a parent/child relationship """

    parent = Indicator.query.get(parent_id)
    if not parent:
        return error_response(404, 'Parent indicator ID not found: {}'.format(parent_id))

    child = Indicator.query.get(child_id)
    if not child:
        return error_response(404, 'Child indicator ID not found: {}'.format(child_id))

    result = parent.remove_child(child)
    if result:
        return '', 204
    else:
        return error_response(400, 'Relationship does not exist')

@bp.route('/indicator/equal/<int:id1>/<int:id2>', methods=['DELETE'])
@api_analyst
def delete_equal(id1, id2):
    """ Deletes an equal to relationship """

    indicator1 = Indicator.query.get(id1)
    if not indicator1:
        return error_response(404, 'id1 indicator not found: {}'.format(id1))

    indicator2 = Indicator.query.get(id2)
    if not indicator2:
        return error_response(404, 'id2 indicator not found: {}'.format(id2))

    result = indicator1.remove_equal(indicator2)
    if result:
        return '', 204
    else:
        return error_message(400, 'Equal to relationship does not exist')
