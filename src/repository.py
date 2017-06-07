from main import db
from models import User, Hopeful, TinderUser, Vote, Match
from sqlalchemy import exists, or_
import pynder
import pickle


class RepoGen:

    @staticmethod
    def add(entity):
        db.session.add(entity)
        db.session.commit()


class RepoTinderUser(RepoGen):

    @staticmethod
    def tinder_user_exists_id(tinder_user_id):
        return db.session.query(exists().where(TinderUser.id == tinder_user_id)).scalar()

    @staticmethod
    def tinder_user_exists(tinder_user):
        return RepoTinderUser.tinder_user_exists_id(tinder_user.id)

    @staticmethod
    def add_tinder_user(tinder_user):
        if RepoTinderUser.tinder_user_exists(tinder_user):
            return
        RepoTinderUser.add(tinder_user)

    @staticmethod
    def get_tinder_user(user_id):
        return db.session.query(TinderUser).filter(TinderUser.id == user_id).first()


class RepoUser(RepoGen):

    @staticmethod
    def user_exists(username):
        return db.session.query(exists().where(User.username == username)).scalar()

    @staticmethod
    def add_user(username, access_token=None, pynder_session=None):
        RepoUser.add(User(username, access_token, pynder_session))

    @staticmethod
    def get_user(username):
        if RepoUser.user_exists(username):
            return db.session.query(User).filter(User.username == username)[0]
        else:
            print("user doesn't exist. can't retrieve")
            return None

    @staticmethod
    def delete_user(username):
        if RepoUser.user_exists(username):
            RepoUser.get_user(username).delete()
            db.session.commit()
        else:
            print("can't delete a user that doesn't exist")

    @staticmethod
    def update_user(username, new_access_token):
        if RepoUser.user_exists(username):
            RepoUser.get_user(username).access_token = new_access_token
            db.session.commit()
        else:
            print("can't update a user that doesn't exist")

    @staticmethod
    def user_has_access_token(username):
        return RepoUser.get_user(username).access_token is not None

    @staticmethod
    def user_has_pynder_session(username):
        pynder_session = RepoUser.get_user(username).pynder_session
        return pynder_session is not None and len(pynder_session) > 0

    @staticmethod
    def dump_pynder_session(username, pynder_session):
        if not RepoUser.user_exists(username):
            RepoUser.add_user(username)

        RepoUser.get_user(username).set_pynder_session(pynder_session)
        print("dumped pynder session to db")

    @staticmethod
    def load_pynder_session(username):
        if not RepoUser.user_exists(username):
            RepoUser.add_user(username)

        user = RepoUser.get_user(username)

        if not RepoUser.user_has_access_token(username):
            print("%r doesn't have an access token; please fix" % user)
            return None

        if not RepoUser.user_has_pynder_session(username):
            pynder_session = RepoUser.create_pynder_session(user.access_token)
            user.set_pynder_session(pickle.dumps(pynder_session))

            print("%r's pynder session is now %r" % (user, user.pynder_session))

        return pickle.loads(user.pynder_session)

    @staticmethod
    def create_pynder_session(fb_token, fb_id=None):
        pynder_session = pynder.Session(facebook_id=fb_id, facebook_token=fb_token)
        return pynder_session


class RepoHopeful(RepoGen):

    @staticmethod
    def hopeful_exists(hash_code):
        return db.session.query(exists().where(Hopeful.hash_code == hash_code)).scalar()

    @staticmethod
    def add_hopeful(hopeful):
        if RepoHopeful.hopeful_exists(hopeful.hash_code):
            return
        RepoHopeful.add(hopeful)

    @staticmethod
    def get_hopeful(hash_code):
        if RepoHopeful.hopeful_exists(hash_code):
            return pickle.loads(db.session.query(Hopeful).filter(Hopeful.hash_code == hash_code)[0].pickled)
        else:
            print("hopeful with hash=%i doesn't exist. can't retrieve" % hash_code)
            return None

    @staticmethod
    def get_all_hopefuls():
        for hopeful in db.session.query(Hopeful).all():
            yield pickle.loads(hopeful.pickled)


class RepoVote(RepoGen):

    @staticmethod
    def vote_exists(vote):
        return db.session.query(exists().where(Vote.hopeful_id == vote.hopeful_id and Vote.voter_id == vote.voter_id)).\
            scalar()

    @staticmethod
    def get_vote(vote):
        return db.session.query(Vote).filter(
            Vote.hopeful_id == vote.hopeful_id and Vote.voter_id == vote.voter_id).first()


class RepoMatch(RepoGen):

    @staticmethod
    def match_exists(person1_id, person2_id):
        result = db.session.query(exists()
                                  .where(or_((Match.person1_id == person1_id and Match.person2_id == person2_id),
                                             (Match.person2_id == person1_id and Match.person1_id == person2_id))))\
            .scalar()
        return result

    @staticmethod
    def get_match(person1_id, person2_id):
        return db.session.query(Match).filter(or_((Match.person1_id == person1_id and Match.person2_id == person2_id),
                                                  (Match.person2_id == person1_id and Match.person1_id == person2_id)))\
            .first()

    @staticmethod
    def set_message_count(person1_id, person2_id, message_count):
        if not RepoMatch.match_exists(person1_id, person2_id):
            return None
        RepoMatch.get_match(person1_id, person2_id).message_count = message_count
        db.session.commit()

    @staticmethod
    def get_message_count(person1_id, person2_id):
        if not RepoMatch.match_exists(person1_id, person2_id):
            return -1
        return RepoMatch.get_match(person1_id, person2_id).message_count
