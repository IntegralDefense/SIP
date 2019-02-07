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


@bp.route('/indicators/<int:parent_id>/<int:child_id>/relationship', methods=['POST'])
@check_if_token_required
@validate_schema(create_schema)
def create_indicator_relationship(parent_id, child_id):
    """ Creates a parent/child relationship between two indicators """

    # Verify the parent ID exists.
    parent_indicator = Indicator.query.get(parent_id)
    if not parent_indicator:
        return error_response(404, 'Parent indicator ID not found: {}'.format(parent_id))

    # Verify the child ID exists.
    child_indicator = Indicator.query.get(child_id)
    if not child_indicator:
        return error_response(404, 'Child indicator ID not found: {}'.format(child_id))

    # Verify the parent and child are not the same.
    if parent_id == child_id:
        return error_response(400, 'Cannot add an indicator to its own children')

    # Try to create the relationship or error if it could not be created.
    result = parent_indicator.add_child(child_indicator)
    if result:
        db.session.commit()
        return '', 204
    else:
        db.session.rollback()
        return error_response(400, 'Child indicator already has a parent')


"""
DELETE
"""


@bp.route('/indicators/<int:parent_id>/<int:child_id>/relationship', methods=['DELETE'])
@check_if_token_required
def delete_indicator_relationship(parent_id, child_id):
    """ Deletes an indicator parent/child relationship. """

    # Verify the parent ID exists.
    parent_indicator = Indicator.query.get(parent_id)
    if not parent_indicator:
        return error_response(404, 'Parent indicator ID not found: {}'.format(parent_id))

    # Verify the child ID exists.
    child_indicator = Indicator.query.get(child_id)
    if not child_indicator:
        return error_response(404, 'Child indicator ID not found: {}'.format(child_id))

    # Verify the parent and child are not the same.
    if parent_id == child_id:
        return error_response(400, 'Parent and child indicators must be different')

    result = parent_indicator.remove_child(child_indicator)
    if result:
        db.session.commit()
        return '', 204
    else:
        db.session.rollback()
        return error_response(400, 'Relationship does not exist')
