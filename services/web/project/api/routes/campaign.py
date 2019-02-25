from flask import current_app, jsonify, request, url_for
from sqlalchemy import exc

from project import db
from project.api import bp
from project.api.decorators import check_if_token_required, validate_json, validate_schema
from project.api.errors import error_response
from project.models import Campaign, CampaignAlias

"""
CREATE
"""

create_schema = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string', 'minLength': 1, 'maxLength': 255},
        'aliases': {
            'type': 'array',
            'items': {'type': 'string', 'minLength': 1, 'maxLength': 255},
            'minItems': 1
        }
    },
    'required': ['name'],
    'additionalProperties': False
}


@bp.route('/campaigns', methods=['POST'])
@check_if_token_required
@validate_json
@validate_schema(create_schema)
def create_campaign():
    """ Creates a new campaign. """

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
    """ Gets a single campaign given its ID. """

    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return error_response(404, 'Campaign ID not found')

    return jsonify(campaign.to_dict())


@bp.route('/campaigns', methods=['GET'])
@check_if_token_required
def read_campaigns():
    """ Gets a list of all the campaigns. """

    data = Campaign.query.all()
    return jsonify([item.to_dict() for item in data])


"""
UPDATE
"""

update_schema = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string', 'minLength': 1, 'maxLength': 255}
    },
    'required': ['name'],
    'additionalProperties': False
}


@bp.route('/campaigns/<int:campaign_id>', methods=['PUT'])
@check_if_token_required
@validate_json
@validate_schema(update_schema)
def update_campaign(campaign_id):
    """ Updates an existing campaign. """

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
    """ Deletes a campaign. """

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
