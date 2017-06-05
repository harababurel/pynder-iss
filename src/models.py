import dateutil
from pynder.constants import SIMPLE_FIELDS

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

UPDATABLE_FIELDS = [
    'gender', 'age_filter_min', 'age_filter_max',
    'distance_filter', 'age_filter_min', 'bio', 'interested_in']


class TinderUser(db.Model):
    __tablename__ = 'tinderuser'

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(20))
    bio = db.Column(db.String(200))
    birth_date = db.Column(db.Date)
    gender = db.Column(db.String(10))
    age_filter_min = db.Column(db.Integer)
    age_filter_max = db.Column(db.Integer)
    distance_filter = db.Column(db.Integer)
    photos = db.relationship('Photo')

    def __init__(self, data):
        for field in SIMPLE_FIELDS:
            setattr(self, field, data.get(field))

        self.photos_obj = [photo for photo in data['photos']]




class Photo(db.Model):
    __tablename__ = 'photos'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    url = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('tinderuser.id'))


    def __init__(self, url, user_id):
        self.url = url
        self.user_id = user_id

