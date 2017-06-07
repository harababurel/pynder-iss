from sqlalchemy import exists

from main import db
from models_components import School, Job


class RepoSchool:

    @staticmethod
    def school_exists(school):
        return db.session.query(exists().where(School.name == school)).scalar()

    @staticmethod
    def get_school(school):
        return db.session.query(School).filter(School.name == school).first()


class RepoJob:

    @staticmethod
    def job_exists(job):
        return db.session.query(exists().where(Job.name == job)).scalar()

    @staticmethod
    def get_job(job):
        return db.session.query(Job).filter(Job.name == job).first()
