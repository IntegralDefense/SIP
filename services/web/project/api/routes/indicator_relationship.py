from project import db
from project.api import bp
from project.api.decorators import check_apikey, validate_schema
from project.api.errors import error_response
from project.api.schemas import null_create
from project.models import Indicator

"""
CREATE
"""


@bp.route('/indicators/<int:parent_id>/<int:child_id>/relationship', methods=['POST'])
@check_apikey
@validate_schema(null_create)
def create_indicator_relationship(parent_id, child_id):
    """ Creates a parent/child relationship between two indicators.

    .. :quickref: Indicator; Creates a parent/child relationship between two indicators.

    **Example request**:

    .. sourcecode:: http

      POST /indicators/1/2/relationship HTTP/1.1
      Host: 127.0.0.1

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 204 No Content

    :reqheader Authorization: Optional Apikey value
    :resheader Content-Type: application/json
    :status 204: Relationship created
    :status 400: Cannot add an indicator to its own children
    :status 400: Child indicator already has a parent
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 404: Indicator ID not found
    """

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
@check_apikey
def delete_indicator_relationship(parent_id, child_id):
    """ Deletes an indicator parent/child relationship.

    .. :quickref: Indicator; Deletes an equal to relationship between two indicators.

    **Example request**:

    .. sourcecode:: http

      DELETE /indicators/1/2/relationship HTTP/1.1
      Host: 127.0.0.1

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 204 No Content

    :reqheader Authorization: Optional Apikey value
    :status 204: Relationship deleted
    :status 400: Parent and child indicators must be different
    :status 401: Invalid role to perform this action
    :status 404: Indicator ID not found
    :status 404: Relationship does not exist
    """

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
        return error_response(404, 'Relationship does not exist')
