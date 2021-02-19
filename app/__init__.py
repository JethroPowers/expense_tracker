from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify, abort, make_response, url_for
import datetime
from sqlalchemy.sql import operators, extract, func
from instance.config import app_config, Config
import os

# initialize sql-alchemy
db = SQLAlchemy()


def create_app(config_name):
    app = FlaskAPI(__name__, instance_relative_config=True)

    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config.from_object(app_config[config_name])
    # for removing trailing slashes enforcement
    app.url_map.strict_slashes = False

    db.init_app(app)

    from .models import ExpenseTracker, User

    @app.route('/expenses/', methods=['POST', 'GET'])
    def expense():
        # Get the access token from the header
        auth_header = request.headers.get('Authorization')
        if auth_header is None:
            response = jsonify({
                'message': f'Authorization header missing',
                'status': 'error'
            })
            response.status_code = 401
            return response
        if auth_header == '':
            response = jsonify({
                'message': f'Please insert Bearer token',
                'status': 'error'
            })
            response.status_code = 401
            return response
        access_token = auth_header.split(" ")
        if len(access_token) < 2:
            response = jsonify({
                'message': f'Authorization token should start with keyword Bearer',
                'status': 'error'
            })
            response.status_code = 401
            return response
        access_token = auth_header.split(" ")[1]

        if access_token:
            # Attempt to decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                # Go ahead and handle the request, the user is authenticated

                if request.method == "POST":
                    name = str(request.data.get('name', ''))
                    amount = str(request.data.get('amount', '')).strip()
                    try:
                        amount_num = float(amount)
                    except ValueError:
                        response = jsonify({
                            'message': f'the amount entered is not a valid number',
                            'status': 'error'
                        })
                        response.status_code = 400
                        return response
                    date_of_expense = str(request.data.get('date_of_expense', '')).strip()
                    try:
                        date = datetime.datetime.strptime(date_of_expense, '%d-%m-%Y')
                    except ValueError:
                        response = jsonify({
                            'message': f'The date {date_of_expense} does not match the format DD-MM-YYYY',
                            'status': 'error'
                        })
                        response.status_code = 400

                        return response

                    if not name:
                        response = jsonify({
                            'message': 'PLease enter a valid name',
                            'status': 'error'
                        })
                        response.status_code = 400

                        return response

                    expense = ExpenseTracker(name=name, amount=amount_num, date_of_expense=date,
                                             belongs_to=user_id)
                    expense.save()
                    response = jsonify({
                        'id': expense.id,
                        'name': expense.name,
                        'amount': expense.amount_spent,
                        'date_of_expense': expense.date_of_expense.strftime('%d-%m-%Y'),
                        'date_created': expense.date_created,
                        'date_modified': expense.date_modified,
                        'belongs_to': expense.belongs_to

                    })
                    response.status_code = 201
                    return response

                else:
                    # GET

                    results = []

                    # get the query string for limit if it exists and for pagination
                    # if the query parameter for limit doesn't exist, 20 is used by default

                    limit = request.args.get('limit', str(Config.DEFAULT_PAGINATION_LIMIT))
                    try:
                        limit = int(limit)
                    except ValueError:
                        # if limit value is gibberish, default to 20
                        limit = Config.DEFAULT_PAGINATION_LIMIT

                    # if limit supplied is greater than 100, display only 100
                    if limit > Config.MAXIMUM_PAGINATION_LIMIT:
                        limit = Config.MAXIMUM_PAGINATION_LIMIT

                    # set the default page to display to 1
                    page = request.args.get('page', '1')

                    try:
                        page = int(page)
                    except ValueError:
                        # if page value is gibberish, default to 1
                        page = 1

                    if limit < 1 or page < 1:
                        return abort(404, 'Page or Limit must be greater than 1')

                    queries = []
                    search_str = request.args.get('name')

                    if search_str:
                        queries.append(ExpenseTracker.name.ilike(f'%{search_str}%'))

                    start_date_str = request.args.get('start_date')

                    if start_date_str:
                        try:
                            start_date = datetime.datetime.strptime(start_date_str, '%d-%m-%Y')
                        except ValueError:
                            response = jsonify({
                                'message': f'The date {start_date_str} does not match the format DD-MM-YYYY',
                                'status': 'error'
                            })
                            response.status_code = 400

                            return response
                        queries.append(ExpenseTracker.date_of_expense >= start_date)

                    end_date_str = request.args.get('end_date')
                    if end_date_str:
                        try:
                            end_date = datetime.datetime.strptime(end_date_str, '%d-%m-%Y')
                        except ValueError:
                            response = jsonify({
                                'message': f'The date {end_date_str} does not match the format DD-MM-YYYY',
                                'status': 'error'
                            })
                            response.status_code = 400

                            return response
                        queries.append(ExpenseTracker.date_of_expense <= end_date)

                    expenses = ExpenseTracker.query.filter_by(belongs_to=user_id).filter(*queries).paginate(page, limit)

                    if page == 1:
                        prev_page = None
                    else:
                        prev_page = url_for('expense') + f'?limit={limit}&page={page - 1}'

                    if page < expenses.pages:
                        next_page = url_for('expense') + f'?limit={limit}&page={page + 1}'
                    else:
                        next_page = None

                    for expense in expenses.items:
                        obj = {
                            'id': expense.id,
                            'name': expense.name,
                            'amount': expense.amount_spent,
                            'date_of_expense': expense.date_of_expense.strftime('%d-%m-%Y'),
                            'date_created': expense.date_created,
                            'date_modified': expense.date_modified,
                            'belongs_to': expense.belongs_to
                        }
                        results.append(obj)

                    return make_response(jsonify({
                        'items': results,
                        'total_items': expenses.total,
                        'total_pages': expenses.pages,
                        'prev_page': prev_page,
                        'next_page': next_page,
                    })), 200

            else:
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                return make_response(jsonify(response)), 401
                #

    @app.route('/expenses/<int:id>', methods=['GET', 'PUT', 'DELETE'])
    def expense_manipulation(id, **kwargs):
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            # Get the user id related to this access token
            user_id = User.decode_token(access_token)

            if not isinstance(user_id, str):
                # If the id is not a string(error), we have a user id
                # Get the bucketlist with the id specified from the URL (<int:id>)
                expense = ExpenseTracker.query.filter_by(id=id, belongs_to=user_id).first()

                if not expense:
                    response = jsonify({
                        'message': f'The Expense with this ID: {id} does not exist',
                        'status': 'error'
                    })
                    response.status_code = 404
                    return response
                if request.method == 'DELETE':
                    expense.delete()
                    return {
                               "message": "Expense {} deleted successfully".format(expense.id)
                           }, 200

                elif request.method == 'PUT':
                    name = str(request.data.get('name', ''))
                    amount = str(request.data.get('amount', '')).strip()
                    if amount:
                        try:
                            amount_num = float(amount)
                        except ValueError:
                            response = jsonify({
                                'message': f'the amount entered is not a valid number',
                                'status': 'error'
                            })
                            response.status_code = 400

                            return response
                        expense.amount_spent = amount_num

                    date_of_expense = str(request.data.get('date_of_expense', '')).strip()
                    if date_of_expense:
                        try:
                            date = datetime.datetime.strptime(date_of_expense, '%d-%m-%Y')
                        except ValueError:
                            response = jsonify({
                                'message': f'The date {date_of_expense} does not match the format DD-MM=YYYY',
                                'status': 'error'
                            })
                            response.status_code = 400

                            return response
                        expense.date_of_expense = date_of_expense
                    if name:
                        expense.name = name
                    else:
                        response = jsonify({
                            'message': 'Please enter a expense name',
                            'status': 'error'
                        })
                        response.status_code = 404
                        return response

                    expense.save()
                    response = jsonify({
                        'id': expense.id,
                        'name': expense.name,
                        'amount': expense.amount_spent,
                        'date_of_expense': expense.date_of_expense.strftime('%d-%m-%Y'),
                        'date_created': expense.date_created,
                        'date_modified': expense.date_modified,
                        'belongs_to': expense.belongs_to

                    })
                    response.status_code = 200
                    return response


                else:
                    # GET
                    response = jsonify({
                        'id': expense.id,
                        'name': expense.name,
                        'amount': expense.amount_spent,
                        'date_of_expense': expense.date_of_expense,
                        'date_created': expense.date_created,
                        'date_modified': expense.date_modified,
                        'belongs_to': expense.belongs_to

                    })
                    response.status_code = 200
                    return response

    @app.route('/monthly_report', methods=['GET'])
    def month_expense():
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            # Get the user id related to this access token
            user_id = User.decode_token(access_token)

            if not isinstance(user_id, str):
                # If the id is not a string(error), we have a user id
                # Get the bucketlist with the id specified from the URL (<int:id>)
                expenses = ExpenseTracker.query.filter_by(belongs_to=user_id).first()

                month = request.args.get('month')
                if month:
                    try:
                        date = datetime.datetime.strptime(month, '%m-%Y')
                    except ValueError:
                        response = jsonify({
                            'message': f'The date {month} does not match the format MM-YYYY',
                            'status': 'error'
                        })
                        response.status_code = 400

                        return response

                expenses = ExpenseTracker.query.with_entities(
                    func.sum(ExpenseTracker.amount_spent), ExpenseTracker.date_of_expense) \
                    .filter_by(belongs_to=user_id) \
                    .filter(extract('year', ExpenseTracker.date_of_expense) == date.year) \
                    .filter(extract('month', ExpenseTracker.date_of_expense) == date.month) \
                    .group_by(ExpenseTracker.date_of_expense)\
                    .order_by(ExpenseTracker.date_of_expense.desc())\
                    .all()
                print(expenses)

                #
                # results = dict()
                # for expense in expenses:
                #     expense_date = expense.date_of_expense.strftime('%d/%m/%Y')
                #     if expense_date in results:
                #         results[expense_date] += expense.amount_spent
                #     else:
                #         results[expense_date] = expense.amount_spent
                #
                #
                results = []
                consolidated_total = 0.0
                # expenses.sort(key=lambda tup: tup[1], reverse=True)
                for total_amount, expense_date in expenses:
                    consolidated_total += total_amount
                    obj = {
                        'date': expense_date.strftime('%d/%m/%Y'),
                        'total_expenses': total_amount
                    }
                    results.append(obj)
                print(consolidated_total)
                return make_response(jsonify({
                    'items': results,
                    'consolidated_total': consolidated_total
                })), 200

    @app.route('/yearly_report', methods=['GET'])
    def year_expense():
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            # Get the user id related to this access token
            user_id = User.decode_token(access_token)

            if not isinstance(user_id, str):
                # If the id is not a string(error), we have a user id
                # Get the bucketlist with the id specified from the URL (<int:id>)
                expenses = ExpenseTracker.query.filter_by(belongs_to=user_id).first()

                year = request.args.get('year')
                if year:
                    try:
                        date = datetime.datetime.strptime(year, '%Y')
                    except ValueError:
                        response = jsonify({
                            'message': f'The date {year} does not match the format YYYY',
                            'status': 'error'
                        })
                        response.status_code = 400

                        return response

                expenses = ExpenseTracker.query.with_entities(
                    func.sum(ExpenseTracker.amount_spent).label("total_amount"), extract('month', ExpenseTracker.date_of_expense), extract('year', ExpenseTracker.date_of_expense)) \
                    .filter_by(belongs_to=user_id) \
                    .filter(extract('year', ExpenseTracker.date_of_expense) == date.year) \
                    .group_by(extract('year', ExpenseTracker.date_of_expense), extract('month', ExpenseTracker.date_of_expense)) \
                    .all()


                consolidated_total = 0.0
                results = []
                for total_amount, month, year in expenses:
                    consolidated_total += total_amount
                    obj = {
                        'month': f'{int(month)}-{int(year)}',
                        'total_expenses': total_amount
                    }
                    results.append(obj)

                return make_response(jsonify({
                    'months': results,
                    'consolidated_total': consolidated_total
                })), 200

    from .auth import auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app
