from app import db


class Tracker(db.Model):
    """This class represents the bucketlist table."""

    __tablename__ = 'expense_Tracker'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    amount_spent = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    def __init__(self, name):
        """initialize with name."""
        self.name = name

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Tracker.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "<Tracker: {}>".format(self.name)