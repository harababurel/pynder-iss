from main import db
from flask_login import UserMixin

import pickle


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    username = db.Column(db.String(50), primary_key=True)
    access_token = db.Column(db.String(300))
    pynder_session = db.Column(db.Binary)

    def __init__(self, username, access_token=None, pynder_session=None):
        self.username = username
        self.access_token = access_token
        self.pynder_session = pynder_session

    def set_pynder_session(self, pynder_session):
        self.pynder_session = pynder_session
        db.session.commit()

    def __repr__(self):
        return '<User %r>' % self.username

class Hopeful(db.Model):
    __tablename__ = 'hopefuls'

    hash_code = db.Column(db.BigInteger, primary_key=True)
    pickled = db.Column(db.Binary)

    def __init__(self, hopeful):
        self.pickled = pickle.dumps(hopeful)
        self.hash_code = hopeful.__hash__()

    def __repr__(self):
        return "<Hopeful %i>" % self.hash_code
