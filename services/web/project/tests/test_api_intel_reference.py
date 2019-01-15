import json

from flask import current_app

from project.tests.base import BaseTestCase
from project.tests.base import TEST_ADMIN_APIKEY, TEST_ANALYST_APIKEY, TEST_INVALID_APIKEY


class TestIntelReference(BaseTestCase):
    """ Tests for the Intel Reference API calls """

    """
    CREATE TESTS
    """

    def test_create_missing_values(self):
        """ Ensure the required parameters are given """

        with self.client:
            current_app.config['POST'] = None

            data = {'reference': 'asdf', 'source': 'asdf'}
            request = self.client.post('/api/intel/reference', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 400)
            self.assertEqual(response['message'], 'Request must include: apikey, reference, source')

            data = {'apikey': TEST_ANALYST_APIKEY, 'source': 'asdf'}
            request = self.client.post('/api/intel/reference', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 400)
            self.assertEqual(response['message'], 'Request must include: apikey, reference, source')

            data = {'apikey': TEST_ANALYST_APIKEY, 'reference': 'asdf'}
            request = self.client.post('/api/intel/reference', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 400)
            self.assertEqual(response['message'], 'Request must include: apikey, reference, source')

    def test_create_duplicate_reference(self):
        """ Ensure duplicate references cannot be created """

        with self.client:
            current_app.config['POST'] = 'analyst'

            data = {'apikey': TEST_ANALYST_APIKEY, 'value': 'asdf'}
            request = self.client.post('/api/intel/source', data=data)
            self.assertEqual(request.status_code, 201)

            data = {'apikey': TEST_ANALYST_APIKEY, 'reference': 'asdf', 'source': 'asdf'}
            request = self.client.post('/api/intel/reference', data=data)
            self.assertEqual(request.status_code, 201)

            data = {'apikey': TEST_ANALYST_APIKEY, 'reference': 'asdf', 'source': 'asdf'}
            request = self.client.post('/api/intel/reference', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 409)
            self.assertEqual(response['message'], 'Intel reference already exists')

    def test_create_nonexistent_source(self):
        """ Ensure a reference cannot be created with a nonexistent source """

        with self.client:
            current_app.config['POST'] = 'analyst'

            data = {'apikey': TEST_ANALYST_APIKEY, 'reference': 'asdf', 'source': 'asdf'}
            request = self.client.post('/api/intel/reference', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 400)
            self.assertEqual(response['message'], 'Intel source not found')

    def test_create_missing_api_key(self):
        """ Ensure an API key is given if the config requires it """

        with self.client:
            current_app.config['POST'] = 'analyst'

            data = {'reference': 'asdf', 'source': 'asdf'}
            request = self.client.post('/api/intel/reference', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 401)
            self.assertEqual(response['message'], 'Bad or missing API key')

    def test_create_invalid_api_key(self):
        """ Ensure an API key not found in the database does not work """

        with self.client:
            current_app.config['POST'] = 'analyst'

            data = {'apikey': TEST_INVALID_APIKEY, 'reference': 'asdf', 'source': 'asdf'}
            request = self.client.post('/api/intel/reference', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 401)
            self.assertEqual(response['message'], 'API user does not exist')

    def test_create_invalid_role(self):
        """ Ensure the given API key has the proper role access """

        with self.client:
            current_app.config['POST'] = 'user_does_not_have_this_role'

            data = {'apikey': TEST_ANALYST_APIKEY, 'reference': 'asdf', 'source': 'asdf'}
            request = self.client.post('/api/intel/reference', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 401)
            self.assertEqual(response['message'], 'Insufficient privileges')

    def test_create(self):
        """ Ensure a proper request actually works """

        with self.client:
            current_app.config['POST'] = 'analyst'

            data = {'apikey': TEST_ANALYST_APIKEY, 'value': 'asdf'}
            request = self.client.post('/api/intel/source', data=data)
            self.assertEqual(request.status_code, 201)

            data = {'apikey': TEST_ANALYST_APIKEY, 'reference': 'asdf', 'source': 'asdf'}
            request = self.client.post('/api/intel/reference', data=data)
            self.assertEqual(request.status_code, 201)

    """
    READ TESTS
    """

    def test_read_nonexistent_id(self):
        """ Ensure a nonexistent ID does not work """

        with self.client:
            current_app.config['GET'] = None

            request = self.client.get('/api/intel/reference/100')
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 404)
            self.assertEqual(response['message'], 'Intel reference ID not found')

    def test_read_missing_api_key(self):
        """ Ensure an API key is given if the config requires it """

        with self.client:
            current_app.config['GET'] = 'analyst'

            request = self.client.get('/api/intel/reference/1')
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 401)
            self.assertEqual(response['message'], 'Bad or missing API key')

    def test_read_invalid_api_key(self):
        """ Ensure an API key not found in the database does not work """

        with self.client:
            current_app.config['GET'] = 'analyst'

            request = self.client.get('/api/intel/reference/1?apikey={}'.format(TEST_INVALID_APIKEY))
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 401)
            self.assertEqual(response['message'], 'API user does not exist')

    def test_read_invalid_role(self):
        """ Ensure the given API key has the proper role access """

        with self.client:
            current_app.config['GET'] = 'user_does_not_have_this_role'

            request = self.client.get('/api/intel/reference/1?apikey={}'.format(TEST_ANALYST_APIKEY))
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 401)
            self.assertEqual(response['message'], 'Insufficient privileges')

    def test_read_all_values(self):
        """ Ensure all values properly return """

        with self.client:
            current_app.config['GET'] = None
            current_app.config['POST'] = 'analyst'

            data = {'apikey': TEST_ANALYST_APIKEY, 'value': 'asdf'}
            request = self.client.post('/api/intel/source', data=data)
            self.assertEqual(request.status_code, 201)

            data = {'apikey': TEST_ANALYST_APIKEY, 'reference': 'asdf', 'source': 'asdf'}
            request = self.client.post('/api/intel/reference', data=data)
            self.assertEqual(request.status_code, 201)

            data = {'apikey': TEST_ANALYST_APIKEY, 'reference': 'asdf2', 'source': 'asdf'}
            request = self.client.post('/api/intel/reference', data=data)
            self.assertEqual(request.status_code, 201)

            data = {'apikey': TEST_ANALYST_APIKEY, 'reference': 'asdf3', 'source': 'asdf'}
            request = self.client.post('/api/intel/reference', data=data)
            self.assertEqual(request.status_code, 201)

            request = self.client.get('/api/intel/reference')
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 200)
            self.assertEqual(len(response), 3)

    def test_read_by_id(self):
        """ Ensure values can be read by their ID """

        with self.client:
            current_app.config['GET'] = None
            current_app.config['POST'] = 'analyst'

            data = {'apikey': TEST_ANALYST_APIKEY, 'value': 'asdf'}
            request = self.client.post('/api/intel/source', data=data)
            self.assertEqual(request.status_code, 201)

            data = {'apikey': TEST_ANALYST_APIKEY, 'reference': 'asdf', 'source': 'asdf'}
            request = self.client.post('/api/intel/reference', data=data)
            self.assertEqual(request.status_code, 201)

            request = self.client.get('/api/intel/reference/1')
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 200)
            self.assertEqual(response['id'], 1)
            self.assertEqual(response['reference'], 'asdf')
            self.assertEqual(response['source'], 'asdf')
            self.assertEqual(response['user'], 'analyst')

    """
    UPDATE TESTS
    """

    def test_update_nonexistent_id(self):
        """ Ensure a nonexistent ID does not work """

        with self.client:
            current_app.config['PUT'] = 'analyst'

            data = {'apikey': TEST_ANALYST_APIKEY, 'reference': 'asdf', 'source': 'asdf'}
            request = self.client.put('/api/intel/reference/100', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 404)
            self.assertEqual(response['message'], 'Intel reference ID not found')

    def test_update_missing_value(self):
        """ Ensure the required parameters are given """

        with self.client:
            current_app.config['POST'] = 'analyst'
            current_app.config['PUT'] = 'analyst'

            data = {'apikey': TEST_ANALYST_APIKEY, 'value': 'asdf'}
            request = self.client.post('/api/intel/source', data=data)
            self.assertEqual(request.status_code, 201)

            data = {'apikey': TEST_ANALYST_APIKEY, 'reference': 'asdf', 'source': 'asdf'}
            request = self.client.post('/api/intel/reference', data=data)
            self.assertEqual(request.status_code, 201)

            data = {'apikey': TEST_ANALYST_APIKEY}
            request = self.client.put('/api/intel/reference/1', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 400)
            self.assertEqual(response['message'], 'Request must include at least reference or source')

    def test_update_duplicate_value(self):
        """ Ensure duplicate references cannot be updated """

        with self.client:
            current_app.config['POST'] = 'analyst'
            current_app.config['PUT'] = 'analyst'

            data = {'apikey': TEST_ANALYST_APIKEY, 'value': 'asdf'}
            request = self.client.post('/api/intel/source', data=data)
            self.assertEqual(request.status_code, 201)

            data = {'apikey': TEST_ANALYST_APIKEY, 'reference': 'asdf', 'source': 'asdf'}
            request = self.client.post('/api/intel/reference', data=data)
            self.assertEqual(request.status_code, 201)

            data = {'apikey': TEST_ANALYST_APIKEY, 'reference': 'asdf', 'source': 'asdf'}
            request = self.client.put('/api/intel/reference/1', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 409)
            self.assertIn(response['message'], 'Intel reference already exists')

    def test_update_missing_api_key(self):
        """ Ensure an API key is given if the config requires it """

        with self.client:
            current_app.config['PUT'] = 'analyst'

            data = {'reference': 'asdf', 'source': 'asdf'}
            request = self.client.put('/api/intel/reference/1', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 401)
            self.assertEqual(response['message'], 'Bad or missing API key')

    def test_update_invalid_api_key(self):
        """ Ensure an API key not found in the database does not work """

        with self.client:
            current_app.config['PUT'] = 'analyst'

            data = {'apikey': TEST_INVALID_APIKEY, 'reference': 'asdf', 'source': 'asdf'}
            request = self.client.put('/api/intel/reference/1', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 401)
            self.assertEqual(response['message'], 'API user does not exist')

    def test_update_invalid_role(self):
        """ Ensure the given API key has the proper role access """

        with self.client:
            current_app.config['PUT'] = 'user_does_not_have_this_role'

            data = {'apikey': TEST_ANALYST_APIKEY, 'reference': 'asdf', 'source': 'asdf'}
            request = self.client.put('/api/intel/reference/1', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 401)
            self.assertEqual(response['message'], 'Insufficient privileges')

    def test_update(self):
        """ Ensure a proper request actually works """

        with self.client:
            current_app.config['GET'] = None
            current_app.config['POST'] = 'analyst'
            current_app.config['PUT'] = 'analyst'

            data = {'apikey': TEST_ANALYST_APIKEY, 'value': 'asdf'}
            request = self.client.post('/api/intel/source', data=data)
            self.assertEqual(request.status_code, 201)

            data = {'apikey': TEST_ANALYST_APIKEY, 'value': 'asdf2'}
            request = self.client.post('/api/intel/source', data=data)
            self.assertEqual(request.status_code, 201)

            data = {'apikey': TEST_ANALYST_APIKEY, 'reference': 'asdf', 'source': 'asdf'}
            request = self.client.post('/api/intel/reference', data=data)
            self.assertEqual(request.status_code, 201)

            data = {'apikey': TEST_ANALYST_APIKEY, 'reference': 'asdf2'}
            request = self.client.put('/api/intel/reference/1', data=data)
            self.assertEqual(request.status_code, 200)

            request = self.client.get('/api/intel/reference/1')
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 200)
            self.assertEqual(response['id'], 1)
            self.assertEqual(response['reference'], 'asdf2')
            self.assertEqual(response['source'], 'asdf')

            data = {'apikey': TEST_ANALYST_APIKEY, 'source': 'asdf2'}
            request = self.client.put('/api/intel/reference/1', data=data)
            self.assertEqual(request.status_code, 200)

            request = self.client.get('/api/intel/reference/1')
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 200)
            self.assertEqual(response['id'], 1)
            self.assertEqual(response['reference'], 'asdf2')
            self.assertEqual(response['source'], 'asdf2')

            data = {'apikey': TEST_ANALYST_APIKEY, 'reference': 'asdf', 'source': 'asdf'}
            request = self.client.put('/api/intel/reference/1', data=data)
            self.assertEqual(request.status_code, 200)

            request = self.client.get('/api/intel/reference/1')
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 200)
            self.assertEqual(response['id'], 1)
            self.assertEqual(response['reference'], 'asdf')
            self.assertEqual(response['source'], 'asdf')

    """
    DELETE TESTS
    """

    def test_delete_nonexistent_id(self):
        """ Ensure a nonexistent ID does not work """

        with self.client:
            current_app.config['DELETE'] = 'admin'

            data = {'apikey': TEST_ADMIN_APIKEY}
            request = self.client.delete('/api/intel/reference/100', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 404)
            self.assertEqual(response['message'], 'Intel reference ID not found')

    def test_delete_missing_api_key(self):
        """ Ensure an API key is given if the config requires it """

        with self.client:
            current_app.config['DELETE'] = 'admin'

            request = self.client.delete('/api/intel/reference/100')
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 401)
            self.assertEqual(response['message'], 'Bad or missing API key')

    def test_delete_invalid_api_key(self):
        """ Ensure an API key not found in the database does not work """

        with self.client:
            current_app.config['DELETE'] = 'admin'

            data = {'apikey': TEST_INVALID_APIKEY}
            request = self.client.delete('/api/intel/reference/1', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 401)
            self.assertEqual(response['message'], 'API user does not exist')

    def test_delete_invalid_role(self):
        """ Ensure the given API key has the proper role access """

        with self.client:
            current_app.config['DELETE'] = 'user_does_not_have_this_role'

            data = {'apikey': TEST_ANALYST_APIKEY}
            request = self.client.delete('/api/intel/reference/1', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 401)
            self.assertEqual(response['message'], 'Insufficient privileges')

    def test_delete(self):
        """ Ensure a proper request actually works """

        with self.client:
            current_app.config['DELETE'] = 'admin'
            current_app.config['GET'] = None
            current_app.config['POST'] = 'analyst'

            data = {'apikey': TEST_ANALYST_APIKEY, 'value': 'asdf'}
            request = self.client.post('/api/intel/source', data=data)
            self.assertEqual(request.status_code, 201)

            data = {'apikey': TEST_ANALYST_APIKEY, 'reference': 'asdf', 'source': 'asdf'}
            request = self.client.post('/api/intel/reference', data=data)
            self.assertEqual(request.status_code, 201)

            data = {'apikey': TEST_ADMIN_APIKEY}
            request = self.client.delete('/api/intel/reference/1', data=data)
            self.assertEqual(request.status_code, 204)

            request = self.client.get('/api/intel/reference/1')
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 404)
            self.assertEqual(response['message'], 'Intel reference ID not found')
