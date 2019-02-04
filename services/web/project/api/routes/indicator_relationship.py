from flask import jsonify, request

from project import db
from project.api import bp
from project.api.decorators import check_if_token_required
from project.api.errors import error_response
from project.models import Indicator

"""
CREATE
"""


@bp.route('/indicators/relationship', methods=['POST'])
@check_if_token_required
def create_indicator_relationship():
    """ Creates a parent/child relationship between two indicators """

    data = request.values or {}

    # Verify the required fields (parent_id and child_id) are present.
    if 'parent_id' not in data or 'child_id' not in data:
        return error_response(400, 'Request must include "parent_id" and "child_id"')

    parent_id = data['parent_id']
    child_id = data['child_id']

    # Verify the parent ID exists.
    parent_indicator = Indicator.query.get(parent_id)
    if not parent_indicator:
        return error_response(404, 'Parent indicator not found')

    # Verify the child ID exists.
    child_indicator = Indicator.query.get(child_id)
    if not child_indicator:
        return error_response(404, 'Child indicator not found')

    # Verify the parent and child are not the same.
    if parent_id == child_id:
        return error_response(400, 'Cannot add indicator to its own children')

    # Try to create the relationship or error if it could not be created.
    result = parent_indicator.add_child(child_indicator)
    if result:
        db.session.commit()
        return '', 204
    else:
        return error_response(400, 'Child indicator already has a parent')


"""
DELETE
"""


@bp.route('/indicators/relationship', methods=['DELETE'])
@check_if_token_required
def delete_indicator_relationship():
    """ Deletes an indicator parent/child relationship. """

    data = request.values or {}

    # Verify the required fields (parent_id and child_id) are present.
    if 'parent_id' not in data or 'child_id' not in data:
        return error_response(400, 'Request must include "parent_id" and "child_id"')

    parent_id = data['parent_id']
    child_id = data['child_id']

    # Verify the parent ID exists.
    parent_indicator = Indicator.query.get(parent_id)
    if not parent_indicator:
        return error_response(404, 'Parent indicator not found')

    # Verify the child ID exists.
    child_indicator = Indicator.query.get(child_id)
    if not child_indicator:
        return error_response(404, 'Child indicator not found')

    # Verify the parent and child are not the same.
    if parent_id == child_id:
        return error_response(400, 'Parent and child indicators must be different')

    result = parent_indicator.remove_child(child_indicator)
    if result:
        db.session.commit()
        return '', 204
    else:
        return error_response(400, 'Relationship does not exist')
