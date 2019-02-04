from flask import jsonify, request

from project import db
from project.api import bp
from project.api.decorators import check_if_token_required
from project.api.errors import error_response
from project.models import Indicator

"""
CREATE
"""


@bp.route('/indicators/equal', methods=['POST'])
@check_if_token_required
def create_indicator_equal():
    """ Creates an equal to relationship between two indicators """

    data = request.values or {}

    # Verify the required fields (parent_id and child_id) are present.
    if 'a_id' not in data or 'b_id' not in data:
        return error_response(400, 'Request must include "a_id" and "b_id"')

    a_id = data['a_id']
    b_id = data['b_id']

    # Verify the a_id exists.
    a_indicator = Indicator.query.get(a_id)
    if not a_indicator:
        return error_response(404, 'a_id indicator not found')

    # Verify the b_id exists.
    b_indicator = Indicator.query.get(b_id)
    if not b_indicator:
        return error_response(404, 'b_id indicator not found')

    # Verify the IDs are not the same.
    if a_id == b_id:
        return error_response(400, 'Cannot make indicator equal to itself')

    # Try to create the relationship or error if it could not be created.
    result = a_indicator.make_equal(b_indicator)
    if result:
        db.session.commit()
        return '', 204
    else:
        return error_response(400, 'The indicators are already equal')


"""
DELETE
"""


@bp.route('/indicators/equal', methods=['DELETE'])
@check_if_token_required
def delete_indicator_equal():
    """ Deletes an equal to relationship between two indicators """

    data = request.values or {}

    # Verify the required fields (parent_id and child_id) are present.
    if 'a_id' not in data or 'b_id' not in data:
        return error_response(400, 'Request must include "a_id" and "b_id"')

    a_id = data['a_id']
    b_id = data['b_id']

    # Verify the a_id exists.
    a_indicator = Indicator.query.get(a_id)
    if not a_indicator:
        return error_response(404, 'a_id indicator not found')

    # Verify the b_id exists.
    b_indicator = Indicator.query.get(b_id)
    if not b_indicator:
        return error_response(404, 'b_id indicator not found')

    # Verify the IDs are not the same.
    if a_id == b_id:
        return error_response(400, 'Indicators must be different')

    result = a_indicator.remove_equal(b_indicator)
    if result:
        db.session.commit()
        return '', 204
    else:
        return error_response(400, 'Relationship does not exist or the indicators are not directly equal')
