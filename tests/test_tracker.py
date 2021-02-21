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
        self.expense = {'name': 'snacks', 'amount': 12.23, 'date_of_expense': '01-01-2021'}


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
        access_token = json.loads(result.data.decode())['access_token']
        res = self.client().post('/expenses/', headers=dict(Authorization="Bearer " + access_token), data=self.expense)
        self.assertEqual(res.status_code, 201)
        results = json.loads(res.data)
        self.assertEqual('snacks', results['name'])

    def test_auth_header_is_None(self):
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        res = self.client().post('/expenses/', data=self.expense)
        self.assertEqual(res.status_code, 401)
        results = json.loads(res.data)
        self.assertEqual(results['message'], 'Authorization header missing')

    def test_missing_bearer_token(self):
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        res = self.client().post('/expenses/', headers=dict(Authorization=""), data=self.expense)
        self.assertEqual(res.status_code, 401)
        results = json.loads(res.data)
        self.assertEqual(results['message'], 'Please insert Bearer token')

    def test_missing_bearer_keyword(self):
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        res = self.client().post('/expenses/', headers=dict(Authorization=access_token), data=self.expense)
        self.assertEqual(res.status_code, 401)
        results = json.loads(res.data)
        self.assertEqual(results['message'], 'Authorization token should start with keyword Bearer')

    def test_invalid_amount(self):
        """Test API can create a Tracker (POST request)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        res = self.client().post('/expenses/', headers=dict(Authorization="Bearer " + access_token), data=
        {'name': 'soda', 'amount': 'cazc', 'date_of_expense': '10-01-2021'})
        self.assertEqual(res.status_code, 400)
        results = json.loads(res.data)
        self.assertEqual(results['message'], 'the amount entered is not a valid number')

    def test_invalid_date(self):
        """Test API can create a Tracker (POST request)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        res = self.client().post('/expenses/', headers=dict(Authorization="Bearer " + access_token), data=
        {'name': 'soda', 'amount': 1233, 'date_of_expense': 'fgjfj'})
        self.assertEqual(res.status_code, 400)
        results = json.loads(res.data)
        self.assertEqual(results['message'], 'The date fgjfj does not match the format DD-MM-YYYY')

    def test_no_name(self):
        """Test API can create a Tracker (POST request)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        res = self.client().post('/expenses/', headers=dict(Authorization="Bearer " + access_token), data=
        {'name': '', 'amount': 1233, 'date_of_expense': '10-01-2021'})
        self.assertEqual(res.status_code, 400)
        results = json.loads(res.data)
        self.assertEqual(results['message'], 'PLease enter a valid name')

    def test_invalid_amount_PUT(self):
        """Test API can create a Tracker (POST request)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        rv = self.client().post('/expenses/', headers=dict(Authorization="Bearer " + access_token), data=self.expense)
        self.assertEqual(rv.status_code, 201)
        res = self.client().put('/expenses/1', headers=dict(Authorization="Bearer " + access_token), data=
        {'name': 'soda', 'amount': 'cazc', 'date_of_expense': '10-01-2021'})
        self.assertEqual(res.status_code, 400)
        results = json.loads(res.data)
        self.assertEqual(results['message'], 'the amount entered is not a valid number')

    def test_invalid_date_PUT(self):
        """Test API can create a Tracker (POST request)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        rv = self.client().post('/expenses/', headers=dict(Authorization="Bearer " + access_token), data=self.expense)
        self.assertEqual(rv.status_code, 201)
        res = self.client().put('/expenses/1', headers=dict(Authorization="Bearer " + access_token), data=
        {'name': 'soda', 'amount': 1233, 'date_of_expense': 'fgjfj'})
        self.assertEqual(res.status_code, 400)
        results = json.loads(res.data)
        self.assertEqual(results['message'], 'The date fgjfj does not match the format DD-MM-YYYY')

    def test_no_name_PUT(self):
        """Test API can create a Tracker (POST request)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        rv = self.client().post('/expenses/', headers=dict(Authorization="Bearer " + access_token), data=self.expense)
        self.assertEqual(rv.status_code, 201)
        res = self.client().put('/expenses/1', headers=dict(Authorization="Bearer " + access_token), data=
        {'name': ''})
        self.assertEqual(res.status_code, 400)
        results = json.loads(res.data)
        self.assertEqual(results['message'], 'PLease enter a valid name')

    def test_api_can_get_all_expenses(self):
        """Test API can get a expense (GET request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        res = self.client().post('/expenses/', headers=dict(Authorization="Bearer " + access_token), data=self.expense)
        self.assertEqual(res.status_code, 201)
        res = self.client().get('/expenses/', headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(res.status_code, 200)
        results = json.loads(res.data)
        self.assertEqual(results['items'][0]['name'], self.expense['name'])

    def test_api_can_get_expense_by_id(self):
        """Test API can get a single expense by using it's id."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        rv = self.client().post('/expenses/', headers=dict(Authorization="Bearer " + access_token), data=self.expense)
        self.assertEqual(rv.status_code, 201)
        result_in_json = json.loads(rv.data.decode('utf-8').replace("'", "\""))
        results = self.client().get(
            '/expenses/{}'.format(result_in_json['id']), headers=dict(Authorization="Bearer " + access_token))
        res = json.loads(results.data)
        self.assertEqual(results.status_code, 200)
        self.assertEqual('snacks', str(res['name']))

    def test_expense_can_be_edited(self):
        """Test API can edit an existing expense. (PUT request)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        rv = self.client().post(
            '/expenses/', headers=dict(Authorization="Bearer " + access_token),
            data=self.expense)
        self.assertEqual(rv.status_code, 201)
        rv = self.client().put(
            '/expenses/1', headers=dict(Authorization="Bearer " + access_token),
            data={
                "name": "chargers"
            })
        self.assertEqual(rv.status_code, 200)
        results = self.client().get('/expenses/1', headers=dict(Authorization="Bearer " + access_token))
        res = json.loads(results.data)
        self.assertEqual('chargers', str(res['name']))

    def test_expense_deletion(self):
        """Test API can delete an existing expense. (DELETE request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        rv = self.client().post(
            '/expenses/', headers=dict(Authorization="Bearer " + access_token),
            data=self.expense)
        self.assertEqual(rv.status_code, 201)
        res = self.client().delete('/expenses/1', headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(res.status_code, 200)
        # Test to see if it exists, should return a 404
        result = self.client().get('/expenses/1', headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 404)

    def test_GET_Search(self):
        """Test API can search for  an existing expense. (get request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        res = self.client().post('/expenses/', headers=dict(Authorization="Bearer " + access_token), data=self.expense)
        self.assertEqual(res.status_code, 201)
        res = self.client().get('/expenses/?name=snacks', headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(res.status_code, 200)
        results = json.loads(res.data)
        self.assertEqual(results['items'][0]['name'], self.expense['name'])


    def test_GET_startdate(self):
        """Test API can get expenses from after start date (GET request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        res = self.client().post('/expenses/', headers=dict(Authorization="Bearer " + access_token), data=self.expense)
        self.assertEqual(res.status_code, 201)
        rv = self.client().post('/expenses/', headers=dict(Authorization="Bearer " + access_token), data=
        {'name': 'soda', 'amount': 1122, 'date_of_expense': '10-01-2021'})
        self.assertEqual(rv.status_code, 201)
        resl = self.client().get('/expenses/?start_date=01-01-2021', headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(resl.status_code, 200)
        results = json.loads(resl.data)
        self.assertEqual(results['items'][0]['date_of_expense'], self.expense['date_of_expense'])

    def test_GET_enddate(self):
        """Test API can get expenses from before the end date (GET request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        res = self.client().post('/expenses/', headers=dict(Authorization="Bearer " + access_token), data=self.expense)
        self.assertEqual(res.status_code, 201)
        rv = self.client().post('/expenses/', headers=dict(Authorization="Bearer " + access_token), data=
        {'name': 'soda', 'amount': 1122, 'date_of_expense': '10-01-2021'})
        self.assertEqual(rv.status_code, 201)
        resl = self.client().get('/expenses/?end_date=03-01-2021', headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(resl.status_code, 200)
        results = json.loads(resl.data)
        self.assertEqual(results['items'][0]['date_of_expense'], self.expense['date_of_expense'])

    def test_GET_startdate_error(self):
        """Test API can get expenses from after start date (GET request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        res = self.client().post('/expenses/', headers=dict(Authorization="Bearer " + access_token), data=self.expense)
        self.assertEqual(res.status_code, 201)
        rv = self.client().post('/expenses/', headers=dict(Authorization="Bearer " + access_token), data=
        {'name': 'soda', 'amount': 1122, 'date_of_expense': '10-01-2021'})
        self.assertEqual(rv.status_code, 201)
        date = '12sjfnj'
        resl = self.client().get(f'/expenses/?start_date={date}', headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(resl.status_code, 400)
        results = json.loads(resl.data)
        self.assertEqual(results['message'], f'The date {date} does not match the format DD-MM-YYYY')

    def test_GET_enddate_error(self):
        """Test API can get expenses from after start date (GET request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        res = self.client().post('/expenses/', headers=dict(Authorization="Bearer " + access_token), data=self.expense)
        self.assertEqual(res.status_code, 201)
        rv = self.client().post('/expenses/', headers=dict(Authorization="Bearer " + access_token), data=
        {'name': 'soda', 'amount': 1122, 'date_of_expense': '10-01-2021'})
        self.assertEqual(rv.status_code, 201)
        date = '12sjfnj'
        resl = self.client().get(f'/expenses/?end_date={date}', headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(resl.status_code, 400)
        results = json.loads(resl.data)
        self.assertEqual(results['message'], f'The date {date} does not match the format DD-MM-YYYY')

    def test_monthly_report(self):
        """Test API can search for  an existing expense. (get request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        res = self.client().post('/expenses/', headers=dict(Authorization="Bearer " + access_token),
                                 data=self.expense)
        self.assertEqual(res.status_code, 201)
        rv = self.client().post('/expenses/', headers=dict(Authorization="Bearer " + access_token), data=
        {'name': 'soda', 'amount': 200, 'date_of_expense': '10-01-2021'})
        self.assertEqual(rv.status_code, 201)
        fetch = self.client().get('/expenses?name=soda', headers=dict(Authorization="Bearer " + access_token))
        result = json.loads(fetch.data)

        consolidated_total = 212.23
        res = self.client().get('/monthly_report?month=01-2021', headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(res.status_code, 200)
        results = json.loads(res.data)
        self.assertEqual(results['consolidated_total'], consolidated_total)

    def test_monthly_report_error(self):
        """Test API can search for  an existing expense. (get request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        res = self.client().post('/expenses/', headers=dict(Authorization="Bearer " + access_token),
                                 data=self.expense)
        self.assertEqual(res.status_code, 201)
        rv = self.client().post('/expenses/', headers=dict(Authorization="Bearer " + access_token), data=
        {'name': 'soda', 'amount': 200, 'date_of_expense': '10-01-2021'})
        month = 4567
        res = self.client().get(f'/monthly_report?month={month}', headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(res.status_code, 400)
        results = json.loads(res.data)
        self.assertEqual(results['message'], f'The date {month} does not match the format MM-YYYY')

    def test_yearly_report(self):
        """Test API can search for  an existing expense. (get request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        res = self.client().post('/expenses/', headers=dict(Authorization="Bearer " + access_token),
                                 data=self.expense)
        self.assertEqual(res.status_code, 201)
        rv = self.client().post('/expenses/', headers=dict(Authorization="Bearer " + access_token), data=
        {'name': 'soda', 'amount': 200, 'date_of_expense': '10-01-2021'})
        consolidated_total = 212.23
        res = self.client().get('/yearly_report?year=2021', headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(res.status_code, 200)
        results = json.loads(res.data)
        self.assertEqual(results['consolidated_total'], consolidated_total)

    def test_yearly_report_error(self):
        """Test API can search for  an existing expense. (get request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        res = self.client().post('/expenses/', headers=dict(Authorization="Bearer " + access_token),
                                 data=self.expense)
        self.assertEqual(res.status_code, 201)
        rv = self.client().post('/expenses/', headers=dict(Authorization="Bearer " + access_token), data=
        {'name': 'soda', 'amount': 200, 'date_of_expense': '10-01-2021'})
        year = 'sdfg'
        res = self.client().get(f'/yearly_report?year={year}', headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(res.status_code, 400)
        results = json.loads(res.data)
        self.assertEqual(results['message'], f'The date {year} does not match the format YYYY')

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
