import dateutil
from pynder.constants import SIMPLE_FIELDS
from sqlalchemy import exists
from sqlalchemy.ext.declarative import declarative_base

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

class UserSchool(db.Model):
    __tablename__ = 'userschool'
    user_id = db.Column(db.String(25), db.ForeignKey('tinderuser.id'), primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), primary_key=True)

    school = db.relationship('School')

    def __init__(self):
        pass

class UserJob(db.Model):
    __tablename__ = 'userjob'

    user_id = db.Column(db.String(25), db.ForeignKey('tinderuser.id'), primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), primary_key=True)

    job = db.relationship('Job')

class TinderUser(db.Model):
    __tablename__ = 'tinderuser'

    id = db.Column(db.String(25), primary_key=True)
    name = db.Column(db.String(20))
    bio = db.Column(db.String(500))
    birth_date = db.Column(db.Date)
    gender = db.Column(db.String(10))
    photos = db.relationship('Photo')

    jobs = db.relationship('UserJob')
    schools = db.relationship('UserSchool')

    def __init__(self, data):
        self.id = data.id

        self.name = data.name[:20]

        self.bio = data.bio[:500]

        if hasattr(data, 'birth_date'):
            self.birth_date = data.birth_date

        self.gender = data.gender

        if hasattr(data, 'photo'):
            for photo in data.photos:
                self.photos.append(Photo(photo, self.id))


        if hasattr(data, 'jobs'):
            for job in data.jobs:
                userjob = UserJob()
                if job_exist(job):
                    userjob.job= get_job(job)
                else:
                    userjob.job = Job(job)
                self.jobs.append(userjob)

        if hasattr(data, 'school'):
            for school in data.schools:
                userschool = UserSchool()
                if school_exist(school):
                    userschool.school = get_school(school)
                else:
                    userschool.school = School(school)

            self.schools.append(userschool)


class Photo(db.Model):
    __tablename__ = 'photos'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    url = db.Column(db.String(200))
    user_id = db.Column(db.String(25), db.ForeignKey('tinderuser.id'))

    def __init__(self, url, user_id):
        self.url = url
        self.user_id = user_id


class Job(db.Model):
    __tablename__ = 'job'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(200))

    def __init__(self, name):
        self.name = name[:200]


class School(db.Model):
    __tablename__ = 'school'

    name = db.Column(db.String(200), unique=True)
    id = db.Column(db.Integer, autoincrement=True,  primary_key=True)

    def __init__(self, name):
        self.name = name[:200]

class Vote(db.Model):
    __tabelename__ = 'vote'

    voter_id = db.Column(db.String(25), db.ForeignKey('tinderuser.id'), primary_key=True)
    hopeful_id = db.Column(db.String(25), db.ForeignKey('tinderuser.id'), primary_key=True)
    value = db.Column(db.String(10))


    def __init__(self, voter, hopeful, value):
        self.voter_id = voter.id
        self.hopeful_id = hopeful.id
        self.value = value


class Match(db.Model):
    __tabelename__ = 'vote'

    person1_id = db.Column(db.String(25), db.ForeignKey('tinderuser.id'), primary_key=True)
    person2_id = db.Column(db.String(25), db.ForeignKey('tinderuser.id'), primary_key=True)
    nr_of_messages = db.Column(db.Integer)

    def __init__(self, person1, person2):
        self.person1_id = person1
        self.person2_id = person2
        self.nr_of_messages = 0

def school_exist(school):
    return db.session.query(exists().where(School.name == school)).scalar()

def get_school(school):
    return db.session.query(School).filter(School.name == school).first()


def job_exist(job):
    return db.session.query(exists().where(Job.name == job)).scalar()

def get_job(job):
    return db.session.query(Job).filter(Job.name == job).first()

