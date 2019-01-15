from flask import jsonify, request, url_for

from project import db
from project.api import bp
from project.api.decorators import check_apikey
from project.api.errors import error_response
from project.models import Campaign, CampaignAlias

"""
CREATE
"""


@bp.route('/campaigns', methods=['POST'])
@check_apikey
def create_campaign():
    """ Creates a new campaign. """

    data = request.values or {}

    # Verify the required fields (name) are present.
    if 'name' not in data:
        return error_response(400, 'Request must include "name"')

    # Verify this name does not already exist.
    existing = Campaign.query.filter_by(name=data['name']).first()
    if existing:
        return error_response(409, 'Campaign already exists')

    # Create and add the new name.
    campaign = Campaign(name=data['name'])
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
@check_apikey
def read_campaign(campaign_id):
    """ Gets a single campaign given its ID. """

    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return error_response(404, 'Campaign ID not found')

    return jsonify(campaign.to_dict())


@bp.route('/campaigns', methods=['GET'])
@check_apikey
def read_campaigns():
    """ Gets a list of all the campaigns. """

    data = Campaign.query.all()
    return jsonify([item.to_dict() for item in data])


"""
UPDATE
"""


@bp.route('/campaigns/<int:campaign_id>', methods=['PUT'])
@check_apikey
def update_campaign(campaign_id):
    """ Updates an existing campaign. """

    data = request.values or {}

    # Verify the ID exists.
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return error_response(404, 'Campaign ID not found')

    # Verify name if one was specified.
    if 'name' in data:

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
@check_apikey
def delete_campaign(campaign_id):
    """ Deletes a campaign. """

    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return error_response(404, 'Campaign ID not found')

    db.session.delete(campaign)
    db.session.commit()

    return '', 204
