from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES


def error_response(status_code, msg=None, location=None):
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if msg:
        payload['msg'] = msg
    response = jsonify(payload)
    response.status_code = status_code
    if location:
        response.headers['Location'] = location
    return response
