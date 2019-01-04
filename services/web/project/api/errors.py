from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES

def error_response(status_code, message=None, location=None):
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if message:
        payload['message'] = message
    response = jsonify(payload)
    response.status_code = status_code
    if location:
        response.headers['Location'] = location
    return response
