from main import db


class Photo(db.Model):
    __tablename__ = 'photos'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    url = db.Column(db.String(200))
    user_id = db.Column(db.String(25), db.ForeignKey('tinderusers.id'))

    def __init__(self, url, user_id):
        self.url = url
        self.user_id = user_id


class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(200))

    def __init__(self, name):
        self.name = name[:200]


class School(db.Model):
    __tablename__ = 'schools'

    name = db.Column(db.String(200), unique=True)
    id = db.Column(db.Integer, autoincrement=True,  primary_key=True)

    def __init__(self, name):
        self.name = name[:200]


class UserSchool(db.Model):
    __tablename__ = 'userschools'

    user_id = db.Column(db.String(25), db.ForeignKey('tinderusers.id'), primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), primary_key=True)

    school = db.relationship('School')

    def __init__(self):
        pass


class UserJob(db.Model):
    __tablename__ = 'userjobs'

    user_id = db.Column(db.String(25), db.ForeignKey('tinderusers.id'), primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), primary_key=True)

    job = db.relationship('Job')