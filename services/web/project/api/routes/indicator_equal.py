from project import db
from project.api import bp
from project.api.decorators import check_if_token_required, validate_schema
from project.api.errors import error_response
from project.models import Indicator

"""
CREATE
"""

create_schema = {
    'type': 'null',
    'properties': {},
    'additionalProperties': False
}


@bp.route('/indicators/<int:a_id>/<int:b_id>/equal', methods=['POST'])
@check_if_token_required
@validate_schema(create_schema)
def create_indicator_equal(a_id, b_id):
    """ Creates an equal to relationship between two indicators """

    # Verify the a_id exists.
    a_indicator = Indicator.query.get(a_id)
    if not a_indicator:
        return error_response(404, 'Indicator ID not found: {}'.format(a_id))

    # Verify the b_id exists.
    b_indicator = Indicator.query.get(b_id)
    if not b_indicator:
        return error_response(404, 'Indicator ID not found: {}'.format(b_id))

    # Verify the IDs are not the same.
    if a_id == b_id:
        return error_response(400, 'Cannot make indicator equal to itself')

    # Try to create the relationship or error if it could not be created.
    result = a_indicator.make_equal(b_indicator)
    if result:
        db.session.commit()
        return '', 204
    else:
        db.session.rollback()
        return error_response(400, 'The indicators are already equal')


"""
DELETE
"""


@bp.route('/indicators/<int:a_id>/<int:b_id>/equal', methods=['DELETE'])
@check_if_token_required
def delete_indicator_equal(a_id, b_id):
    """ Deletes an equal to relationship between two indicators """

    # Verify the a_id exists.
    a_indicator = Indicator.query.get(a_id)
    if not a_indicator:
        return error_response(404, 'Indicator ID not found: {}'.format(a_id))

    # Verify the b_id exists.
    b_indicator = Indicator.query.get(b_id)
    if not b_indicator:
        return error_response(404, 'Indicator ID not found: {}'.format(b_id))

    # Verify the IDs are not the same.
    if a_id == b_id:
        return error_response(400, 'Indicators must be different')

    result = a_indicator.remove_equal(b_indicator)
    if result:
        db.session.commit()
        return '', 204
    else:
        db.session.rollback()
        return error_response(400, 'Relationship does not exist or the indicators are not directly equal')
