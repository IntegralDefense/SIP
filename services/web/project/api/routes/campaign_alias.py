from flask import jsonify, request, url_for
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
        'alias': {'type': 'string', 'minLength': 1, 'maxLength': 255},
        'campaign': {'type': 'string', 'minLength': 1, 'maxLength': 255}
    },
    'required': ['alias', 'campaign'],
    'additionalProperties': False
}


@bp.route('/campaigns/alias', methods=['POST'])
@check_if_token_required
@validate_json
@validate_schema(create_schema)
def create_campaign_alias():
    """ Creates a new campaign alias. """

    data = request.get_json()

    # Verify the campaign exists.
    campaign = Campaign.query.filter_by(name=data['campaign']).first()
    if not campaign:
        return error_response(400, 'Campaign does not exist')

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
@check_if_token_required
def read_campaign_alias(campaign_alias_id):
    """ Gets a single campaign alias given its ID. """

    campaign_alias = CampaignAlias.query.get(campaign_alias_id)
    if not campaign_alias:
        return error_response(404, 'Campaign alias ID not found')

    return jsonify(campaign_alias.to_dict())


@bp.route('/campaigns/alias', methods=['GET'])
@check_if_token_required
def read_campaign_aliases():
    """ Gets a list of all the campaign aliases. """

    data = CampaignAlias.query.all()
    return jsonify([item.to_dict() for item in data])


"""
UPDATE
"""

update_schema = {
    'type': 'object',
    'properties': {
        'alias': {'type': 'string', 'minLength': 1, 'maxLength': 255},
        'campaign': {'type': 'string', 'minLength': 1, 'maxLength': 255}
    },
    'additionalProperties': False
}


@bp.route('/campaigns/alias/<int:campaign_alias_id>', methods=['PUT'])
@check_if_token_required
@validate_json
@validate_schema(update_schema)
def update_campaign_alias(campaign_alias_id):
    """ Updates an existing campaign alias. """

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
@check_if_token_required
def delete_campaign_alias(campaign_alias_id):
    """ Deletes a campaign alias. """

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
