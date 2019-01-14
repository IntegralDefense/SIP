import json

from flask import current_app

from project.tests.base import BaseTestCase
from project.tests.base import config
from project.tests.base import TEST_APIKEY, TEST_ADMIN_APIKEY, TEST_ANALYST_APIKEY


class TestIndicator(BaseTestCase):
    """ Tests for the Indicator API calls """

    def create_indicators(self, num_indicators):
        """ Helper function to create num_indicators amount of indicators """

        for x in range(num_indicators):
            indicator = {'apikey': TEST_APIKEY, 'type': list(config['indicator_type'])[0], 'value': x}
            self.client.post('/api/indicators', data=indicator)

    def test_missing_apikey(self):
        """ Ensure there is an API key present """

        with self.client:
            indicator = {'type': 'blah', 'value': 'blah'}
            request = self.client.post('/api/indicators', data=indicator)
            data = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 401)
            self.assertEqual(data['message'], 'Bad or missing API key')

    def test_insufficient_apikey(self):
        """ Ensure the API key has the correct privileges """

        with self.client:
            indicator = {'apikey': TEST_ADMIN_APIKEY, 'type': 'blah', 'value': 'blah'}
            request = self.client.post('/api/indicators', data=indicator)
            data = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 401)
            self.assertEqual(data['message'], 'Insufficient privileges')

    def test_missing_type(self):
        """ Ensure the type parameter is specified """

        with self.client:
            indicator = {'apikey': TEST_APIKEY, 'value': 'blah'}
            request = self.client.post('/api/indicators', data=indicator)
            data = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 400)
            self.assertEqual(data['message'], 'Request must include "type" and "value"')

    def test_missing_value(self):
        """ Ensure the value parameter is specified """

        with self.client:
            indicator = {'apikey': TEST_APIKEY, 'type': 'blah'}
            request = self.client.post('/api/indicators', data=indicator)
            data = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 400)
            self.assertEqual(data['message'], 'Request must include "type" and "value"')

    def test_default_values(self):
        """ Ensure the various default values are correct from the setup.ini file """

        with self.client:
            indicator = {'apikey': TEST_APIKEY, 'type': list(config['indicator_type'])[0], 'value': 1}
            request = self.client.post('/api/indicators', data=indicator)
            data = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 201)
            self.assertEqual(data['campaigns'], [])
            self.assertEqual(data['case_sensitive'], False)
            self.assertEqual(data['children'], [])
            self.assertEqual(data['confidence'], list(config['indicator_confidence'])[0])
            self.assertEqual(data['equal'], [])
            self.assertEqual(data['impact'], list(config['indicator_impact'])[0])
            self.assertEqual(data['references'], [])
            self.assertEqual(data['status'], list(config['indicator_status'])[0])
            self.assertEqual(data['substring'], False)
            self.assertEqual(data['tags'], [])

    def test_invalid_confidence(self):
        """ Ensure the given confidence is valid in the database """

        with self.client:
            indicator = {'apikey': TEST_APIKEY, 'type': list(config['indicator_type'])[0], 'value': 'blah',
                         'confidence': 'asdfasdfasdf'}
            request = self.client.post('/api/indicators', data=indicator)
            data = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 400)
            self.assertIn('confidence must be one of', data['message'])

    def test_invalid_impact(self):
        """ Ensure the given impact is valid in the database """

        with self.client:
            indicator = {'apikey': TEST_APIKEY, 'type': list(config['indicator_type'])[0], 'value': 'blah',
                         'impact': 'asdfasdfasdf'}
            request = self.client.post('/api/indicators', data=indicator)
            data = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 400)
            self.assertIn('impact must be one of', data['message'])

    def test_invalid_status(self):
        """ Ensure the given status is valid in the database """

        with self.client:
            indicator = {'apikey': TEST_APIKEY, 'type': list(config['indicator_type'])[0], 'value': 'blah',
                         'status': 'asdfasdfasdf'}
            request = self.client.post('/api/indicators', data=indicator)
            data = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 400)
            self.assertIn('status must be one of', data['message'])

    def test_duplicate_indicator(self):
        """ Ensure you cannot create duplicate type+value indicators """

        with self.client:
            indicator = {'apikey': TEST_APIKEY, 'type': list(config['indicator_type'])[0], 'value': 'blah'}
            request = self.client.post('/api/indicators', data=indicator)
            request2 = self.client.post('/api/indicators', data=indicator)
            data = json.loads(request2.data.decode())
            self.assertEqual(request.status_code, 201)
            self.assertEqual(request2.status_code, 409)
            self.assertEqual(data['message'], 'Indicator already exists: 1')

    def test_read_indicator(self):
        """ Ensure you can read an indicator by its ID """

        with self.client:
            self.create_indicators(1)

            request = self.client.get('/api/indicators/1')
            data = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 200)
            self.assertEqual(data['id'], 1)

            request = self.client.get('/api/indicators/2')
            data = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 404)
            self.assertEqual(data['message'], 'Indicator ID not found: 2')

    def test_paginate_indicators(self):
        """ Ensure the indicator pagination works properly """

        with self.client:
            self.create_indicators(100)

            request = self.client.get('/api/indicators?per_page=10')
            data = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 200)
            self.assertEqual(data['_meta']['total_items'], 100)
            self.assertEqual(data['_meta']['total_pages'], 10)
            results = set()
            for ind in data['items']:
                results.add(ind['value'])
            while data['_links']['next']:
                request = self.client.get(data['_links']['next'])
                data = json.loads(request.data.decode())
                self.assertEqual(request.status_code, 200)
                for ind in data['items']:
                    results.add(ind['value'])

            self.assertEqual(len(results), 100)

    def test_filter_by_value(self):
        """ Ensure you can filter the indicators by their values """

        with self.client:
            self.create_indicators(100)

            request = self.client.get('/api/indicators?value=1')
            data = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 200)
            self.assertEqual(data['_meta']['total_items'], 19)

    def test_update_indicator(self):
        """ Ensure you can update an existing indicator """

        with self.client:
            self.create_indicators(1)

            self.assertNotEqual(list(config['indicator_confidence'])[0], list(config['indicator_confidence'])[-1])
            self.assertNotEqual(list(config['indicator_impact'])[0], list(config['indicator_impact'])[-1])
            self.assertNotEqual(list(config['indicator_status'])[0], list(config['indicator_status'])[-1])

            request = self.client.get('/api/indicators/1')
            orig = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 200)
            self.assertEqual(orig['confidence'], list(config['indicator_confidence'])[0])
            self.assertEqual(orig['impact'], list(config['indicator_impact'])[0])
            self.assertEqual(orig['status'], list(config['indicator_status'])[0])

            update = {'apikey': TEST_APIKEY,
                      'confidence': list(config['indicator_confidence'])[-1],
                      'impact': list(config['indicator_impact'])[-1],
                      'status': list(config['indicator_status'])[-1]}
            request = self.client.put('/api/indicators/1', data=update)
            self.assertEqual(request.status_code, 200)

            request = self.client.get('/api/indicators/1')
            new = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 200)
            self.assertEqual(new['confidence'], list(config['indicator_confidence'])[-1])
            self.assertEqual(new['impact'], list(config['indicator_impact'])[-1])
            self.assertEqual(new['status'], list(config['indicator_status'])[-1])

    def test_update_invalid_indicator(self):
        """ Ensure you cannot update an invalid indicator """

        with self.client:
            self.create_indicators(1)

            update = {'apikey': TEST_APIKEY,
                      'confidence': list(config['indicator_confidence'])[-1],
                      'impact': list(config['indicator_impact'])[-1],
                      'status': list(config['indicator_status'])[-1]}
            request = self.client.put('/api/indicators/2', data=update)
            data = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 404)
            self.assertEqual(data['message'], 'Indicator ID not found: 2')

    def test_update_invalid_confidence(self):
        """ Ensure you cannot update an existing indicator with an invalid confidence """

        with self.client:
            self.create_indicators(1)

            update = {'apikey': TEST_APIKEY, 'confidence': 'asdfasdfasdf'}
            request = self.client.put('/api/indicators/1', data=update)
            data = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 400)
            self.assertIn('confidence must be one of', data['message'])

    def test_update_invalid_impact(self):
        """ Ensure you cannot update an existing indicator with an invalid impact """

        with self.client:
            self.create_indicators(1)

            update = {'apikey': TEST_APIKEY, 'impact': 'asdfasdfasdf'}
            request = self.client.put('/api/indicators/1', data=update)
            data = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 400)
            self.assertIn('impact must be one of', data['message'])

    def test_update_invalid_status(self):
        """ Ensure you cannot update an existing indicator with an invalid status """

        with self.client:
            self.create_indicators(1)

            update = {'apikey': TEST_APIKEY, 'status': 'asdfasdfasdf'}
            request = self.client.put('/api/indicators/1', data=update)
            data = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 400)
            self.assertIn('status must be one of', data['message'])

    def test_delete_indicator(self):
        """ Ensure you can delete an indicator """

        with self.client:
            self.create_indicators(1)

            request = self.client.get('/api/indicators/1')
            self.assertEqual(request.status_code, 200)

            delete = {'apikey': TEST_APIKEY}
            request = self.client.delete('/api/indicators/1', data=delete)
            self.assertEqual(request.status_code, 204)

            request = self.client.get('/api/indicators/1')
            self.assertEqual(request.status_code, 404)

    def test_delete_invalid_indicator(self):
        """ Ensure you cannot delete an invalid indicator """

        with self.client:
            self.create_indicators(1)

            request = self.client.get('/api/indicators/1')
            self.assertEqual(request.status_code, 200)

            delete = {'apikey': TEST_APIKEY}
            request = self.client.delete('/api/indicators/2', data=delete)
            data = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 404)
            self.assertEqual(data['message'], 'Indicator ID not found: 2')

    def test_delete_indicator_without_admin(self):
        """ Ensure that an analyst cannot delete an indicator """

        with self.client:
            self.create_indicators(1)

            request = self.client.get('/api/indicators/1')
            self.assertEqual(request.status_code, 200)

            delete = {'apikey': TEST_ANALYST_APIKEY}
            request = self.client.delete('/api/indicators/1', data=delete)
            data = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 401)
            self.assertEqual(data['message'], 'Insufficient privileges')

    def test_create_relationship(self):
        """ Ensure you can create a parent/child relationship """

        with self.client:
            self.create_indicators(4)

            # Ensure all 4 indicators have empty relationships
            request = self.client.get('/api/indicators/1')
            indicator1 = json.loads(request.data.decode())
            self.assertEqual(indicator1['children'], [])
            self.assertEqual(indicator1['all_children'], [])
            self.assertEqual(indicator1['parent'], None)

            request = self.client.get('/api/indicators/2')
            indicator2 = json.loads(request.data.decode())
            self.assertEqual(indicator2['children'], [])
            self.assertEqual(indicator2['all_children'], [])
            self.assertEqual(indicator2['parent'], None)

            request = self.client.get('/api/indicators/3')
            indicator3 = json.loads(request.data.decode())
            self.assertEqual(indicator3['children'], [])
            self.assertEqual(indicator3['all_children'], [])
            self.assertEqual(indicator3['parent'], None)

            request = self.client.get('/api/indicators/4')
            indicator4 = json.loads(request.data.decode())
            self.assertEqual(indicator4['children'], [])
            self.assertEqual(indicator4['all_children'], [])
            self.assertEqual(indicator4['parent'], None)

            # Create relationships
            relationship = {'apikey': TEST_APIKEY, 'parent_id': 1, 'child_id': 2}
            request = self.client.post('/api/indicators/relationship', data=relationship)
            self.assertEqual(request.status_code, 204)

            relationship = {'apikey': TEST_APIKEY, 'parent_id': 2, 'child_id': 3}
            request = self.client.post('/api/indicators/relationship', data=relationship)
            self.assertEqual(request.status_code, 204)

            relationship = {'apikey': TEST_APIKEY, 'parent_id': 2, 'child_id': 4}
            request = self.client.post('/api/indicators/relationship', data=relationship)
            self.assertEqual(request.status_code, 204)

            """
            The relationships now look as follows:
    
            1
             \
              2
              |\
              3 4
            """

            # Verify direct and indirect relationships
            request = self.client.get('/api/indicators/1')
            indicator1 = json.loads(request.data.decode())
            self.assertEqual(indicator1['children'], [2])
            self.assertEqual(indicator1['all_children'], [2, 3, 4])
            self.assertEqual(indicator1['parent'], None)

            request = self.client.get('/api/indicators/2')
            indicator2 = json.loads(request.data.decode())
            self.assertEqual(indicator2['children'], [3, 4])
            self.assertEqual(indicator2['all_children'], [3, 4])
            self.assertEqual(indicator2['parent'], 1)

            request = self.client.get('/api/indicators/3')
            indicator3 = json.loads(request.data.decode())
            self.assertEqual(indicator3['children'], [])
            self.assertEqual(indicator3['all_children'], [])
            self.assertEqual(indicator3['parent'], 2)

            request = self.client.get('/api/indicators/4')
            indicator4 = json.loads(request.data.decode())
            self.assertEqual(indicator4['children'], [])
            self.assertEqual(indicator4['all_children'], [])
            self.assertEqual(indicator4['parent'], 2)

            # Try to make a relationship with nonexistent indicators.
            relationship = {'apikey': TEST_APIKEY, 'parent_id': 5, 'child_id': 6}
            request = self.client.post('/api/indicators/relationship', data=relationship)
            data = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 404)
            self.assertIn('indicator not found', data['message'])

            # Try and add an indicator as its own child.
            # This shouldn't do anything.
            relationship = {'apikey': TEST_APIKEY, 'parent_id': 1, 'child_id': 1}
            request = self.client.post('/api/indicators/relationship', data=relationship)
            data = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 400)
            self.assertEqual(data['message'], 'Cannot add indicator to its own children')

            # Try to add a child to a second parent.
            # This shouldn't do anything since it's okay to be a single-parent.
            relationship = {'apikey': TEST_APIKEY, 'parent_id': 1, 'child_id': 3}
            request = self.client.post('/api/indicators/relationship', data=relationship)
            data = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 400)
            self.assertEqual(data['message'], 'Child indicator already has a parent')

            # Remove relationship and emancipate a child.
            relationship = {'apikey': TEST_APIKEY, 'parent_id': 1, 'child_id': 2}
            request = self.client.delete('/api/indicators/relationship', data=relationship)
            self.assertEqual(request.status_code, 204)

            """
            The relationships now look as follows:

            1

              2
              |\
              3 4
            """

            # Verify direct and indirect relationships
            request = self.client.get('/api/indicators/1')
            indicator1 = json.loads(request.data.decode())
            self.assertEqual(indicator1['children'], [])
            self.assertEqual(indicator1['all_children'], [])
            self.assertEqual(indicator1['parent'], None)

            request = self.client.get('/api/indicators/2')
            indicator2 = json.loads(request.data.decode())
            self.assertEqual(indicator2['children'], [3, 4])
            self.assertEqual(indicator2['all_children'], [3, 4])
            self.assertEqual(indicator2['parent'], None)

            request = self.client.get('/api/indicators/3')
            indicator3 = json.loads(request.data.decode())
            self.assertEqual(indicator3['children'], [])
            self.assertEqual(indicator3['all_children'], [])
            self.assertEqual(indicator3['parent'], 2)

            request = self.client.get('/api/indicators/4')
            indicator4 = json.loads(request.data.decode())
            self.assertEqual(indicator4['children'], [])
            self.assertEqual(indicator4['all_children'], [])
            self.assertEqual(indicator4['parent'], 2)

    def test_create_equal(self):
        """ Ensure you can create an equal to relationship """

        with self.client:
            self.create_indicators(4)

            # Ensure all 4 indicators have empty relationships
            request = self.client.get('/api/indicators/1')
            indicator1 = json.loads(request.data.decode())
            self.assertEqual(indicator1['equal'], [])
            self.assertEqual(indicator1['all_equal'], [])

            request = self.client.get('/api/indicators/2')
            indicator2 = json.loads(request.data.decode())
            self.assertEqual(indicator2['equal'], [])
            self.assertEqual(indicator2['all_equal'], [])

            request = self.client.get('/api/indicators/3')
            indicator3 = json.loads(request.data.decode())
            self.assertEqual(indicator3['equal'], [])
            self.assertEqual(indicator3['all_equal'], [])

            request = self.client.get('/api/indicators/4')
            indicator4 = json.loads(request.data.decode())
            self.assertEqual(indicator4['equal'], [])
            self.assertEqual(indicator4['all_equal'], [])

            # Create relationships
            equal = {'apikey': TEST_APIKEY, 'a_id': 1, 'b_id': 2}
            request = self.client.post('/api/indicators/equal', data=equal)
            self.assertEqual(request.status_code, 204)

            equal = {'apikey': TEST_APIKEY, 'a_id': 2, 'b_id': 3}
            request = self.client.post('/api/indicators/equal', data=equal)
            self.assertEqual(request.status_code, 204)

            equal = {'apikey': TEST_APIKEY, 'a_id': 1, 'b_id': 4}
            request = self.client.post('/api/indicators/equal', data=equal)
            self.assertEqual(request.status_code, 204)

            """
            The relationships now look as follows:

            1 - 2 - 3
             \
              4
            """

            # Verify direct and indirect relationships
            request = self.client.get('/api/indicators/1')
            indicator1 = json.loads(request.data.decode())
            self.assertEqual(indicator1['equal'], [2, 4])
            self.assertEqual(indicator1['all_equal'], [2, 3, 4])

            request = self.client.get('/api/indicators/2')
            indicator2 = json.loads(request.data.decode())
            self.assertEqual(indicator2['equal'], [1, 3])
            self.assertEqual(indicator2['all_equal'], [1, 3, 4])

            request = self.client.get('/api/indicators/3')
            indicator3 = json.loads(request.data.decode())
            self.assertEqual(indicator3['equal'], [2])
            self.assertEqual(indicator3['all_equal'], [1, 2, 4])

            request = self.client.get('/api/indicators/4')
            indicator4 = json.loads(request.data.decode())
            self.assertEqual(indicator4['equal'], [1])
            self.assertEqual(indicator4['all_equal'], [1, 2, 3])

            # Try to make a relationship with nonexistent indicators.
            equal = {'apikey': TEST_APIKEY, 'a_id': 5, 'b_id': 6}
            request = self.client.post('/api/indicators/equal', data=equal)
            data = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 404)
            self.assertIn('indicator not found', data['message'])

            # Try to make an indicator equal to itself.
            # This shouldn't work.
            equal = {'apikey': TEST_APIKEY, 'a_id': 1, 'b_id': 1}
            request = self.client.post('/api/indicators/equal', data=equal)
            data = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 400)
            self.assertEqual(data['message'], 'Cannot make indicator equal to itself')

            # Try to add a redundant indirect relationship
            # This shouldn't do anything since 3 is already indirectly equal to 4.
            equal = {'apikey': TEST_APIKEY, 'a_id': 3, 'b_id': 4}
            request = self.client.post('/api/indicators/equal', data=equal)
            data = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 400)
            self.assertEqual(data['message'], 'The indicators are already equal')

            # Remove a relationship
            equal = {'apikey': TEST_APIKEY, 'a_id': 1, 'b_id': 2}
            request = self.client.delete('/api/indicators/equal', data=equal)
            self.assertEqual(request.status_code, 204)

            """
            The relationships now look as follows:

            1   2 - 3
             \
              4
            """

            # Verify direct and indirect relationships
            request = self.client.get('/api/indicators/1')
            indicator1 = json.loads(request.data.decode())
            self.assertEqual(indicator1['equal'], [4])
            self.assertEqual(indicator1['all_equal'], [4])

            request = self.client.get('/api/indicators/2')
            indicator2 = json.loads(request.data.decode())
            self.assertEqual(indicator2['equal'], [3])
            self.assertEqual(indicator2['all_equal'], [3])

            request = self.client.get('/api/indicators/3')
            indicator3 = json.loads(request.data.decode())
            self.assertEqual(indicator3['equal'], [2])
            self.assertEqual(indicator3['all_equal'], [2])

            request = self.client.get('/api/indicators/4')
            indicator4 = json.loads(request.data.decode())
            self.assertEqual(indicator4['equal'], [1])
            self.assertEqual(indicator4['all_equal'], [1])
