from flask import jsonify, request, url_for
from sqlalchemy import exc

from project import db
from project.api import bp
from project.api.decorators import check_apikey, validate_json, validate_schema
from project.api.errors import error_response
from project.api.schemas import campaign_alias_create, campaign_alias_update
from project.models import Campaign, CampaignAlias

"""
CREATE
"""


@bp.route('/campaigns/alias', methods=['POST'])
@check_apikey
@validate_json
@validate_schema(campaign_alias_create)
def create_campaign_alias():
    """ Creates a new campaign alias.
    
    .. :quickref: CampaignAlias; Creates a new campaign alias.

    **Example request**:

    .. sourcecode:: http

      POST /campaigns/alias HTTP/1.1
      Host: 127.0.0.1
      Content-Type: application/json

      {
        "alias": "icanhaz",
        "campaign": "LOLcats"
      }

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json

      {
        "id": 1,
        "alias": "icanhaz",
        "campaign": "LOLcats"
      }

    :reqheader Authorization: Optional Apikey value
    :resheader Content-Type: application/json
    :status 201: Campaign alias created
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 404: Campaign does not exist
    :status 409: Campaign alias already exists
    :status 409: Campaign alias cannot be the same as its name
    """

    data = request.get_json()

    # Verify the campaign exists.
    campaign = Campaign.query.filter_by(name=data['campaign']).first()
    if not campaign:
        return error_response(404, 'Campaign does not exist')

    # Verify this alias does not already exist.
    existing = CampaignAlias.query.filter_by(alias=data['alias']).first()
    if existing:
        return error_response(409, 'Campaign alias already exists')

    # Verify the alias is not the same as the campaign name.
    if data['alias'].lower() == data['campaign'].lower():
        return error_response(409, 'Campaign alias cannot be the same as its name')

    # Create and add the new name.
    campaign_alias = CampaignAlias(alias=data['alias'], campaign=campaign)
    db.session.add(campaign_alias)
    db.session.commit()

    response = jsonify(campaign_alias.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.read_campaign_alias', campaign_alias_id=campaign_alias.id)
    return response


"""
READ
"""


@bp.route('/campaigns/alias/<int:campaign_alias_id>', methods=['GET'])
@check_apikey
def read_campaign_alias(campaign_alias_id):
    """ Gets a single campaign alias given its ID.
    
    .. :quickref: CampaignAlias; Gets a single campaign alias given its ID.

    **Example request**:

    .. sourcecode:: http

      GET /campaigns/alias/1 HTTP/1.1
      Host: 127.0.0.1
      Accept: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "id": 1,
        "alias": "icanhaz",
        "campaign": "LOLcats"
      }

    :reqheader Authorization: Optional Apikey value
    :resheader Content-Type: application/json
    :status 200: Campaign alias found
    :status 401: Invalid role to perform this action
    :status 404: Campaign alias ID not found
    """

    campaign_alias = CampaignAlias.query.get(campaign_alias_id)
    if not campaign_alias:
        return error_response(404, 'Campaign alias ID not found')

    return jsonify(campaign_alias.to_dict())


@bp.route('/campaigns/alias', methods=['GET'])
@check_apikey
def read_campaign_aliases():
    """ Gets a list of all the campaign aliases.
    
    .. :quickref: CampaignAlias; Gets a list of all the campaign aliases.

    **Example request**:

    .. sourcecode:: http

      GET /campaigns/alias HTTP/1.1
      Host: 127.0.0.1
      Accept: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
        {
          "id": 1,
          "alias": "icanhaz",
          "campaign": "LOLcats"
        },
        {
          "id": 2,
          "alias": "Dino",
          "campaign": "Riders"
        }
      ]

    :reqheader Authorization: Optional Apikey value
    :resheader Content-Type: application/json
    :status 200: Campaign aliases found
    :status 401: Invalid role to perform this action
    """

    data = CampaignAlias.query.all()
    return jsonify([item.to_dict() for item in data])


"""
UPDATE
"""


@bp.route('/campaigns/alias/<int:campaign_alias_id>', methods=['PUT'])
@check_apikey
@validate_json
@validate_schema(campaign_alias_update)
def update_campaign_alias(campaign_alias_id):
    """ Updates an existing campaign alias.
    
    .. :quickref: CampaignAlias; Updates an existing campaign alias.

    **Example request**:

    .. sourcecode:: http

      PUT /campaigns/alias/1 HTTP/1.1
      Host: 127.0.0.1
      Content-Type: application/json

      {
        "alias": "Dino",
        "campaign": "Riders"
      }

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "id": 1,
        "alias": "Dino",
        "campaign": "Riders"
      }

    :reqheader Authorization: Optional Apikey value
    :resheader Content-Type: application/json
    :status 200: Campaign alias updated
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 404: Campaign alias ID not found
    :status 404: Campaign not found
    :status 409: Campaign alias already exists
    :status 409: Campaign alias cannot be the same as its name
    """

    data = request.get_json()

    # Verify the ID exists.
    campaign_alias = CampaignAlias.query.get(campaign_alias_id)
    if not campaign_alias:
        return error_response(404, 'Campaign alias ID not found')

    # Verify alias if one was specified.
    if 'alias' in data:

        # Verify the alias is not the same as the campaign name.
        if data['alias'].lower() == campaign_alias.campaign.name.lower():
            return error_response(409, 'Campaign alias cannot be the same as its name')

        # Verify this alias does not already exist.
        existing = CampaignAlias.query.filter_by(alias=data['alias']).first()
        if existing:
            return error_response(409, 'Campaign alias already exists')
        else:
            campaign_alias.alias = data['alias']

    # Verify campaign if one was specified.
    if 'campaign' in data:

        # Verify the campaign exists.
        campaign = Campaign.query.filter_by(name=data['campaign']).first()
        if not campaign:
            return error_response(404, 'Campaign not found')

        # Update the campaign.
        campaign_alias.campaign = campaign

    # Save the changes.
    db.session.commit()

    response = jsonify(campaign_alias.to_dict())
    return response


"""
DELETE
"""


@bp.route('/campaigns/alias/<int:campaign_alias_id>', methods=['DELETE'])
@check_apikey
def delete_campaign_alias(campaign_alias_id):
    """ Deletes a campaign alias.
    
    .. :quickref: CampaignAlias; Deletes an campaign alias.

    **Example request**:

    .. sourcecode:: http

      DELETE /campaigns/alias/1 HTTP/1.1
      Host: 127.0.0.1

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 204 No Content

    :reqheader Authorization: Optional Apikey value
    :status 204: Campaign alias deleted
    :status 401: Invalid role to perform this action
    :status 404: Campaign alias ID not found
    :status 409: Unable to delete campaign alias due to foreign key constraints
    """

    campaign_alias = CampaignAlias.query.get(campaign_alias_id)
    if not campaign_alias:
        return error_response(404, 'Campaign alias ID not found')

    try:
        db.session.delete(campaign_alias)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        return error_response(409, 'Unable to delete campaign alias due to foreign key constraints')

    return '', 204
