# Expense Tracker
The Expense tracker is python flask API that tracks the expenses of a user and is 
able to generate monthly and yearly reports

## Pre-requisites
* [Python 3.7](https://www.python.org/downloads/release/python-379/)
* [Git](https://git-scm.com/downloads)
* [PostgreSQL](https://www.postgresql.org/download/windows/)
* [pip](https://pip.pypa.io/en/stable/reference/pip_download/)



Ensure you have installed PostgreSQL in your computer and 
it's server is running locally on port 5432

## API Features 
* Register and Sign up
* Creating multiple expenses 
* Token-based authentication
* Changing aspects of existing expenses such as the name, date and amount
* Monthly and yearly reports and a consolidated total
* Search feature

## Using the API

Export environment variables. This as well starts the virtual environment venv

```
set FLASK_APP=run.py
set SECRET=some-very-long-string-of-random-characters-CHANGE-TO-YOUR-LIKING
set APP_SETTINGS=development
set DATABASE_URL="postgresql://localhost/expense_api"
```


Install dependencies in the virtual environment

```
pip install -r requirements.txt
```
### Endpoints
Register Endpoint
```
localhost:5000/auth/register
```

Login Endpoint
```
localhost:5000/auth/login
```

Expenses Endpoint
```
localhost:5000/expenses
```

Expense manipulation endpoint
```
localhost:5000/expenses/<id>
```

Monthly report endpoint
```
localhost:5000/monthly_report
```

Yearly report endpoint
```
localhost:5000/yearly_report
```

### Running the tests

```
python manage.py test
```


### Viewing the test coverage

```
python manage.py cov
```

## Author

**Jethro Xavier Powers**



