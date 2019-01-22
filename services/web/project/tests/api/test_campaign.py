import json


def test_create(client):
    data = {'name': 'asdf'}
    request = client.post('/api/campaigns', data=data)
    response = json.loads(request.data.decode())
    print(response)
    assert request.status_code == 201
