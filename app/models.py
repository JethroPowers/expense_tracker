from app import db
from sqlalchemy import and_
from flask_bcrypt import Bcrypt
import jwt
from datetime import datetime, timedelta
from instance.config import Config

class User(db.Model):
    """This class defines the users table """

    __tablename__ = 'users'

    # Define the columns of the users table, starting with the primary key
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    expenses = db.relationship(
        'ExpenseTracker', order_by='ExpenseTracker.id', cascade="all, delete-orphan")

    def __init__(self, email, password):
        """Initialize the user with an email and a password."""
        self.email = email
        self.password = Bcrypt().generate_password_hash(password).decode()

    def password_is_valid(self, password):
        """
        Checks the password against it's hash to validates the user's password
        """
        return Bcrypt().check_password_hash(self.password, password)

    def save(self):
        """Save a user to the database.
        This includes creating a new user and editing one.
        """
        db.session.add(self)
        db.session.commit()

    def generate_token(self, user_id):
        """ Generates the access token"""

        try:
            # set up a payload with an expiration time
            payload = {
                'exp': datetime.utcnow() + timedelta(hours=5),
                'iat': datetime.utcnow(),
                'sub': user_id
            }
            # create the byte string token using the payload and the SECRET key
            jwt_string = jwt.encode(
                payload,
                Config.SECRET,
                algorithm='HS256'
            )
            return jwt_string

        except Exception as e:
            # return an error in string format if an exception occurs
            return str(e)

    @staticmethod
    def decode_token(token):
        """Decodes the access token from the Authorization header."""
        try:
            # try to decode the token using our SECRET variable
            payload = jwt.decode(token, Config.SECRET)
            return payload['sub']
        except jwt.ExpiredSignatureError:
            # the token is expired, return an error string
            return "Expired token. Please login to get a new token"
        except jwt.InvalidTokenError:
            # the token is invalid, return an error string
            return "Invalid token. Please register or login"


class ExpenseTracker(db.Model):
    """This class represents the Expense tracker table."""

    __tablename__ = 'Expense_Tracker'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    amount_spent = db.Column(db.Float)
    date_of_expense = db.Column(db.Date)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())
    belongs_to = db.Column(db.Integer, db.ForeignKey(User.id))

    def __init__(self, name, amount, date_of_expense, belongs_to):
        """initialize with name."""
        self.name = name
        self.amount_spent = amount
        self.date_of_expense = date_of_expense
        self.belongs_to = belongs_to

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return ExpenseTracker.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def is_name_exists(expense_name, expense_id):
        num_rows = ExpenseTracker.query.filter(and_(ExpenseTracker.name == expense_name,
                                             ExpenseTracker.expense_id == expense_id)).count()
        return num_rows > 0

    @staticmethod
    def is_name_exists_except_id(expense_name, id, expense_id):
        num_rows = ExpenseTracker.query.filter(
            and_(ExpenseTracker.name == expense_name, ExpenseTracker.id != id,
                 ExpenseTracker.id == expense_id)).count()

        return num_rows > 0

    def __repr__(self):
        return "<Tracker: {}>".format(self.name)
