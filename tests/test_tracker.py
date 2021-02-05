# test_tracker.py
import unittest
import os
import json
from app import create_app, db


class TrackerTestCase(unittest.TestCase):
    """This class represents the tracker test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.expense = {'name': 'snacks', 'amount': 12.23, 'date_of_expense': '10-01-2020'}

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

    def register_user(self, email="user@test.com", password="test1234"):
        """This helper method helps register a test user."""
        user_data = {
            'email': email,
            'password': password
        }
        return self.client().post('/auth/register', data=user_data)

    def login_user(self, email="user@test.com", password="test1234"):
        """This helper method helps log in a test user."""
        user_data = {
            'email': email,
            'password': password
        }
        return self.client().post('/auth/login', data=user_data)

        ############################################
        ##### ALL OUR TESTS METHODS LIE HERE #######


    def test_expenses_creation(self):
        """Test API can create a Tracker (POST request)"""
        self.register_user()
        result = self.login_user()
        res = self.client().post('/expenses/', data=self.expense)
        self.assertEqual(res.status_code, 201)
        results = json.loads(res.data)
        self.assertEqual('snacks', results['name'])

    def test_api_can_get_all_expenses(self):
        """Test API can get a expense (GET request)."""
        self.register_user()
        result = self.login_user()
        res = self.client().post('/expenses/', data=self.expense)
        self.assertEqual(res.status_code, 201)
        res = self.client().get('/expenses/')
        self.assertEqual(res.status_code, 200)
        results = json.loads(res.data)
        self.assertEqual(results[0]['name'], self.expense['name'])

    def test_api_can_get_expense_by_id(self):
        """Test API can get a single expense by using it's id."""
        self.register_user()
        result = self.login_user()
        rv = self.client().post('/expenses/', data=self.expense)
        self.assertEqual(rv.status_code, 201)
        result_in_json = json.loads(rv.data.decode('utf-8').replace("'", "\""))
        results = self.client().get(
            '/expenses/{}'.format(result_in_json['id']))
        res = json.loads(results.data)
        self.assertEqual(results.status_code, 200)
        self.assertEqual('snacks', str(res['name']))

    def test_expense_can_be_edited(self):
        """Test API can edit an existing expense. (PUT request)"""
        self.register_user()
        result = self.login_user()
        rv = self.client().post(
            '/expenses/',
            data=self.expense)
        self.assertEqual(rv.status_code, 201)
        rv = self.client().put(
            '/expenses/1',
            data={
                "name": "chargers"
            })
        self.assertEqual(rv.status_code, 200)
        results = self.client().get('/expenses/1')
        res = json.loads(results.data)
        self.assertEqual('chargers', str(res['name']))

    def test_expense_deletion(self):
        """Test API can delete an existing expense. (DELETE request)."""
        self.register_user()
        result = self.login_user()
        rv = self.client().post(
            '/expenses/',
            data=self.expense)
        self.assertEqual(rv.status_code, 201)
        res = self.client().delete('/expenses/1')
        self.assertEqual(res.status_code, 200)
        # Test to see if it exists, should return a 404
        result = self.client().get('/expenses/1')
        self.assertEqual(result.status_code, 404)


    # Make the tests conveniently executable
    if __name__ == "__main__":
        unittest.main()

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()