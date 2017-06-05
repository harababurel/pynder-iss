from main import db
from models import User, Hopeful
from sqlalchemy import exists
import pynder
import pickle


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
    return get_user(username).pynder_session is not None


def dump_pynder_session(username, pynder_session):
    if not user_exists(username):
        create_user(username)

    get_user(username).set_pynder_session(pynder_session)
    print("dumped pynder session to db")


def load_pynder_session(username):
    if not user_exists(username):
        create_user(username)

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
