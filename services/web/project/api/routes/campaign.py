from flask import current_app, jsonify, request, url_for
from sqlalchemy import exc

from project import db
from project.api import bp
from project.api.decorators import check_if_token_required, validate_json, validate_schema
from project.api.errors import error_response
from project.api.schemas import campaign_create, campaign_update
from project.models import Campaign, CampaignAlias

"""
CREATE
"""


@bp.route('/campaigns', methods=['POST'])
@check_if_token_required
@validate_json
@validate_schema(campaign_create)
def create_campaign():
    """ Creates a new campaign.
    
    .. :quickref: Campaign; Creates a new campaign.

    **Example request**:

    .. sourcecode:: http

      POST /campaigns HTTP/1.1
      Host: 127.0.0.1
      Content-Type: application/json

      {
        "name": "LOLcats",
        "aliases": ["icanhaz"]
      }

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json

      {
        "id": 1,
        "aliases": ["icanhaz"],
        "created_time": "Thu, 28 Feb 2019 17:10:44 GMT",
        "modified_time": "Thu, 28 Feb 2019 17:10:44 GMT",
        "name": "LOLcats"
      }

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 201: Campaign created
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 404: Campaign alias not found
    :status 409: Campaign already exists
    """

    data = request.get_json()

    # Verify this name does not already exist.
    existing = Campaign.query.filter_by(name=data['name']).first()
    if existing:
        return error_response(409, 'Campaign already exists')

    # Create and add the new name.
    campaign = Campaign(name=data['name'])

    # Verify any aliases that were specified.
    if 'aliases' in data:
        for alias in data['aliases']:
            campaign_alias = CampaignAlias.query.filter_by(alias=alias).first()
            if not campaign_alias:
                if current_app.config['CAMPAIGN_AUTO_CREATE_CAMPAIGNALIAS']:
                    campaign_alias = CampaignAlias(alias=alias, campaign=campaign)
                    db.session.add(campaign_alias)
                else:
                    return error_response(404, 'Campaign alias not found: {}'.format(alias))

            campaign.aliases.append(campaign_alias)

    db.session.add(campaign)
    db.session.commit()

    response = jsonify(campaign.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.read_campaign', campaign_id=campaign.id)
    return response


"""
READ
"""


@bp.route('/campaigns/<int:campaign_id>', methods=['GET'])
@check_if_token_required
def read_campaign(campaign_id):
    """ Gets a single campaign given its ID.
    
    .. :quickref: Campaign; Gets a single campaign given its ID.

    **Example request**:

    .. sourcecode:: http

      GET /campaigns/1 HTTP/1.1
      Host: 127.0.0.1
      Accept: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "id": 1,
        "aliases": ["icanhaz"],
        "created_time": "Thu, 28 Feb 2019 17:10:44 GMT",
        "modified_time": "Thu, 28 Feb 2019 17:10:44 GMT",
        "name": "LOLcats"
      }

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 200: Campaign found
    :status 401: Invalid role to perform this action
    :status 404: Campaign ID not found
    """

    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return error_response(404, 'Campaign ID not found')

    return jsonify(campaign.to_dict())


@bp.route('/campaigns', methods=['GET'])
@check_if_token_required
def read_campaigns():
    """ Gets a list of all the campaigns.
    
    .. :quickref: Campaign; Gets a list of all the campaigns.

    **Example request**:

    .. sourcecode:: http

      GET /campaigns HTTP/1.1
      Host: 127.0.0.1
      Accept: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
        {
          "id": 1,
          "aliases": ["icanhaz"],
          "created_time": "Thu, 28 Feb 2019 17:10:44 GMT",
          "modified_time": "Thu, 28 Feb 2019 17:10:44 GMT",
          "name": "LOLcats"
        },
        {
          "id": 2,
          "aliases": [],
          "created_time": "Thu, 28 Feb 2019 17:11:37 GMT",
          "modified_time": "Thu, 28 Feb 2019 17:11:37 GMT",
          "name": "Derpsters"
        }
      ]

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 200: Campaigns found
    :status 401: Invalid role to perform this action
    """

    data = Campaign.query.all()
    return jsonify([item.to_dict() for item in data])


"""
UPDATE
"""


@bp.route('/campaigns/<int:campaign_id>', methods=['PUT'])
@check_if_token_required
@validate_json
@validate_schema(campaign_update)
def update_campaign(campaign_id):
    """ Updates an existing campaign.
    
    .. :quickref: Campaign; Updates an existing campaign.

    **Example request**:

    .. sourcecode:: http

      PUT /campaigns/1 HTTP/1.1
      Host: 127.0.0.1
      Content-Type: application/json

      {
        "name": "Derpsters",
      }

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "id": 1,
        "aliases": ["icanhaz"],
        "created_time": "Thu, 28 Feb 2019 17:10:44 GMT",
        "modified_time": "Thu, 28 Feb 2019 17:18:29 GMT",
        "name": "Derpsters"
      }

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 200: Campaign updated
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 404: Campaign ID not found
    :status 409: Campaign already exists
    """

    data = request.get_json()

    # Verify the ID exists.
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return error_response(404, 'Campaign ID not found')

    # Verify this name does not already exist.
    existing = Campaign.query.filter_by(name=data['name']).first()
    if existing:
        return error_response(409, 'Campaign already exists')
    else:
        campaign.name = data['name']

    # Save the changes.
    db.session.commit()

    response = jsonify(campaign.to_dict())
    return response


"""
DELETE
"""


@bp.route('/campaigns/<int:campaign_id>', methods=['DELETE'])
@check_if_token_required
def delete_campaign(campaign_id):
    """ Deletes a campaign.
    
    .. :quickref: Campaign; Deletes a campaign.

    **Example request**:

    .. sourcecode:: http

      DELETE /campaigns/1 HTTP/1.1
      Host: 127.0.0.1

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 204 No Content

    :reqheader Authorization: Optional JWT Bearer token
    :status 204: Campaign deleted
    :status 401: Invalid role to perform this action
    :status 404: Campaign ID not found
    :status 409: Unable to delete campaign due to foreign key constraints
    """

    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return error_response(404, 'Campaign ID not found')

    try:
        db.session.delete(campaign)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        return error_response(409, 'Unable to delete campaign due to foreign key constraints')

    return '', 204
