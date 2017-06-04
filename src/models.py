from main import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    username = db.Column(db.String(50), primary_key=True)
    access_token = db.Column(db.String(100))

    def __init__(self, username, access_token):
        self.username = username
        self.access_token = access_token

    def get_username(self):
        return self.username

    def get_token(self):
        return self.access_token

    def __repr__(self):
        return '<User %r>' % self.username
