from flask import jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_refresh_token_required, jwt_required, fresh_jwt_required
from flask_security.utils import verify_password

from project import jwt
from project.api.errors import error_response
from project.auth import bp
from project.models import User


@jwt.user_claims_loader
def add_claims_to_access_token(identity):
    user = User.query.filter_by(username=identity).first()
    return {'roles': [r.name for r in user.roles]}


@bp.route('/auth', methods=['POST'])
def auth_user():
    """ Authenticate a user and generate fresh access and refresh tokens """

    data = request.values or {}

    # Verify the required fields are present.
    if 'username' not in data or 'password' not in data:
        return error_response(400, 'Request must include: username, password')

    # Verify the username exists.
    user = User.query.filter_by(username=data['username']).first()
    if not user:
        return error_response(401, 'User does not exist')

    # Verify the user is active.
    if not user.active:
        return error_response(401, 'User is inactive')

    # Verify the password.
    if verify_password(data['password'], user.password):

        # Create the tokens.
        access_token = create_access_token(identity=user.username, fresh=True)
        refresh_token = create_refresh_token(identity=user.username)

        return jsonify({'access_token': access_token, 'refresh_token': refresh_token})
    else:
        return error_response(401, 'Invalid password')


@bp.route('/auth-fresh', methods=['POST'])
def auth_user_fresh():
    """ Authenticate a user and generate a fresh access token """

    data = request.values or {}

    # Verify the required fields are present.
    if 'username' not in data or 'password' not in data:
        return error_response(400, 'Request must include: username, password')

    # Verify the username exists.
    user = User.query.filter_by(username=data['username']).first()
    if not user:
        return error_response(401, 'User does not exist')

    # Verify the user is active.
    if not user.active:
        return error_response(401, 'User is inactive')

    # Verify the password.
    if verify_password(data['password'], user.password):

        # Create the token.
        access_token = create_access_token(identity=user.username, fresh=True)

        return jsonify({'access_token': access_token})
    else:
        return error_response(401, 'Invalid password')


@bp.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    """ Generates a non-fresh token without needing to re-authenticate """

    current_user = get_jwt_identity()
    return jsonify({'access_token': create_access_token(identity=current_user, fresh=False)})
