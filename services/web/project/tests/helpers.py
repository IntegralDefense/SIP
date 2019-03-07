import json


def create_auth_header(token):
    return {'Authorization': 'Bearer {}'.format(token)}


def obtain_token(client, username, password):
    request = client.post('/auth', data={'username': username, 'password': password})
    response = json.loads(request.data.decode())
    return response['access_token'], response['refresh_token']


def create_campaign(client, campaign, aliases=[]):
    data = {'name': campaign}
    if aliases:
        data['aliases'] = aliases
    request = client.post('/api/campaigns', json=data)
    response = json.loads(request.data.decode())
    return request, response


def create_campaign_alias(client, alias, campaign):
    data = {'alias': alias, 'campaign': campaign}
    request = client.post('/api/campaigns/alias', json=data)
    response = json.loads(request.data.decode())
    return request, response


def create_indicator(client, _type, value, username, campaigns=[], case_sensitive=False, confidence='', impact='',
                     intel_reference='', intel_source='', status='', substring=False, tags=[]):
    create_indicator_type(client, _type)

    if not confidence:
        confidence = 'LOW'
    create_indicator_confidence(client, confidence)

    if not impact:
        impact = 'LOW'
    create_indicator_impact(client, impact)

    if not status:
        status = 'New'
    create_indicator_status(client, status)

    data = {'case_sensitive': case_sensitive, 'confidence': confidence, 'impact': impact, 'status': status,
            'substring': substring, 'type': _type, 'username': username, 'value': value}
    if campaigns:
        for campaign in campaigns:
            create_campaign(client, campaign)
        data['campaigns'] = campaigns
    if tags:
        for tag in tags:
            create_tag(client, tag)
        data['tags'] = tags
    if intel_reference and intel_source:
        create_intel_reference(client, username, intel_source, intel_reference)
        data['references'] = [{'source': intel_source, 'reference': intel_reference}]

    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    return request, response


def create_indicator_confidence(client, confidence):
    data = {'value': confidence}
    request = client.post('/api/indicators/confidence', json=data)
    response = json.loads(request.data.decode())
    return request, response


def create_indicator_impact(client, impact):
    data = {'value': impact}
    request = client.post('/api/indicators/impact', json=data)
    response = json.loads(request.data.decode())
    return request, response


def create_indicator_status(client, status):
    data = {'value': status}
    request = client.post('/api/indicators/status', json=data)
    response = json.loads(request.data.decode())
    return request, response


def create_indicator_type(client, _type):
    data = {'value': _type}
    request = client.post('/api/indicators/type', json=data)
    response = json.loads(request.data.decode())
    return request, response


def create_intel_reference(client, username, source, reference):
    create_intel_source(client, source)

    data = {'username': username, 'reference': reference, 'source': source}
    request = client.post('/api/intel/reference', json=data)
    response = json.loads(request.data.decode())
    return request, response


def create_intel_source(client, source):
    data = {'value': source}
    request = client.post('/api/intel/source', json=data)
    response = json.loads(request.data.decode())
    return request, response


def create_role(client, role):
    access_token, refresh_token = obtain_token(client, 'admin', 'admin')
    headers = create_auth_header(access_token)

    data = {'name': role}
    request = client.post('/api/roles', json=data, headers=headers)
    response = json.loads(request.data.decode())
    return request, response


def create_tag(client, tag):
    data = {'value': tag}
    request = client.post('/api/tags', json=data)
    response = json.loads(request.data.decode())
    return request, response


def create_user(client, email, first_name, last_name, password, roles, username):
    access_token, refresh_token = obtain_token(client, 'admin', 'admin')
    headers = create_auth_header(access_token)

    data = {'email': email, 'first_name': first_name, 'last_name': last_name,
            'password': password, 'roles': roles, 'username': username}
    request = client.post('/api/users', json=data, headers=headers)
    response = json.loads(request.data.decode())
    return request, response
