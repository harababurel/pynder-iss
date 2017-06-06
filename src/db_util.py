from main import db
from models import User, Hopeful, TinderUser, Vote, Match
from sqlalchemy import exists, or_
import pynder
import pickle


def tinder_user_exist(tinder_user):
    return db.session.query(exists().where(TinderUser.id == tinder_user.id)).scalar()


def add_tinder_user(tinder_user):
    if tinder_user_exist(tinder_user):
        return
    db.session.add(tinder_user)
    db.session.commit()


def get_tinder_user(user_id):
    return db.session.query(TinderUser).filter(TinderUser.id == user_id).first()


def user_exists(username):
    return db.session.query(exists().where(User.username == username)).scalar()


def hopeful_exists(hash_code):
    return db.session.query(exists().where(Hopeful.hash_code == hash_code)).scalar()


def add_user(username, access_token=None, pynder_session=None):
    db.session.add(User(username, access_token, pynder_session))
    db.session.commit()


def add_hopeful(hopeful):
    if not hopeful_exists(hopeful.hash_code):
        db.session.add(hopeful)
        db.session.commit()


def get_user(username):
    if user_exists(username):
        return db.session.query(User).filter(User.username == username)[0]
    else:
        print("user doesn't exist. can't retrieve")
        return None


def get_hopeful(hash_code):
    if hopeful_exists(hash_code):
        return pickle.loads(db.session.query(Hopeful).filter(Hopeful.hash_code == hash_code)[0].pickled)
    else:
        print("hopeful with hash=%i doesn't exist. can't retrieve" % hash_code)
        return None


def get_all_hopefuls():
    for hopeful in db.session.query(Hopeful).all():
        yield pickle.loads(hopeful.pickled)


def delete_user(username):
    if user_exists(username):
        get_user(username).delete()
        db.session.commit()
    else:
        print("can't delete a user that doesn't exist")


def update_user(username, new_access_token):
    if user_exists(username):
        get_user(username).access_token = new_access_token
        db.session.commit()
    else:
        print("can't update a user that doesn't exist")


def user_has_access_token(username):
    return get_user(username).access_token is not None


def user_has_pynder_session(username):
    pynder_session = get_user(username).pynder_session
    return pynder_session is not None and len(pynder_session) > 0


def dump_pynder_session(username, pynder_session):
    if not user_exists(username):
        add_user(username)

    get_user(username).set_pynder_session(pynder_session)
    print("dumped pynder session to db")


def load_pynder_session(username):
    if not user_exists(username):
        add_user(username)

    user = get_user(username)

    if not user_has_access_token(username):
        print("%r doesn't have an access token; please fix" % user)
        return None

    if not user_has_pynder_session(username):
        pynder_session = create_pynder_session(user.access_token)
        user.set_pynder_session(pickle.dumps(pynder_session))

        print("%r's pynder session is now %r" % (user, user.pynder_session))

    return pickle.loads(user.pynder_session)


def create_pynder_session(fb_token, fb_id=None):
    pynder_session = pynder.Session(facebook_id=fb_id, facebook_token=fb_token)
    return pynder_session


def add(entity):
    db.session.add(entity)
    db.session.commit()


def vote_exists(vote):
    return db.session.query(exists().where(Vote.hopeful_id == vote.hopeful_id and Vote.voter_id == vote.voter_id)).\
        scalar()


def match_exists(person1_id, person2_id):
    result = db.session.query(exists()
                              .where(or_((Match.person1_id == person1_id and Match.person2_id == person2_id),
                                         (Match.person2_id == person1_id and Match.person1_id == person2_id)))).scalar()
    return result


def get_vote(vote):
    return db.session.query(Vote).filter(Vote.hopeful_id == vote.hopeful_id and Vote.voter_id == vote.voter_id).first()


def get_match(person1_id, person2_id):
    return db.session.query(Match).filter(or_((Match.person1_id == person1_id and Match.person2_id == person2_id),
                                              (Match.person2_id == person1_id and Match.person1_id == person2_id))).\
        first()


def set_message_count(person1_id, person2_id, message_count):
    if not match_exists(person1_id, person2_id):
        return None
    get_match(person1_id, person2_id).message_count = message_count
    db.session.commit()


def get_message_count(person1_id, person2_id):
    if not match_exists(person1_id, person2_id):
        return -1
    return get_match(person1_id, person2_id).message_count
