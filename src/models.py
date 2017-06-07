from models_components import Photo, UserJob, Job, UserSchool, School
from repository_components import RepoSchool, RepoJob
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


class TinderUser(db.Model):
    __tablename__ = 'tinderusers'

    id = db.Column(db.String(25), primary_key=True)
    name = db.Column(db.String(20))
    bio = db.Column(db.String(500))
    birth_date = db.Column(db.Date)
    gender = db.Column(db.String(10))
    photos = db.relationship('Photo')

    jobs = db.relationship('UserJob')
    schools = db.relationship('UserSchool')

    def __init__(self, data):
        with db.session.no_autoflush:
            self.id = data.id

            self.name = data.name[:20]

            self.bio = data.bio[:500]

            if hasattr(data, 'birth_date'):
                self.birth_date = data.birth_date

            self.gender = data.gender

            if hasattr(data, 'photos'):
                for photo in data.photos:
                    self.photos.append(Photo(photo, self.id))

            if hasattr(data, 'jobs'):
                for job in data.jobs:
                    userjob = UserJob()
                    if RepoJob.job_exists(job):
                        userjob.job = RepoJob.get_job(job)
                    else:
                        userjob.job = Job(job)
                    self.jobs.append(userjob)

            if hasattr(data, 'schools'):
                for school in data.schools:
                    userschool = UserSchool()
                    if RepoSchool.school_exists(school):
                        userschool.school = RepoSchool.get_school(school)
                    else:
                        userschool.school = School(school)

                    self.schools.append(userschool)


class Vote(db.Model):
    __tablename__ = 'votes'

    voter_id = db.Column(db.String(25), db.ForeignKey('tinderusers.id'), primary_key=True)
    hopeful_id = db.Column(db.String(25), db.ForeignKey('tinderusers.id'), primary_key=True)
    value = db.Column(db.String(10))

    def __init__(self, voter, hopeful, value):
        self.voter_id = voter.id
        self.hopeful_id = hopeful.id
        self.value = value


class Match(db.Model):
    __tablename__ = 'matches'

    person1_id = db.Column(db.String(25), db.ForeignKey('tinderusers.id'), primary_key=True)
    person2_id = db.Column(db.String(25), db.ForeignKey('tinderusers.id'), primary_key=True)
    message_count = db.Column(db.Integer)

    def __init__(self, person1, person2):
        self.person1_id = person1
        self.person2_id = person2
        self.message_count = 0
