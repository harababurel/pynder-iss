from flask import request, session, g, escape, render_template, abort, redirect, url_for, flash
from pynder.models import Profile
from collections import defaultdict
from pprint import pformat

from form_util import SettingsForm
from main import app
from config import config
from fb_auth import get_access_token
import itertools
import db_util
import pickle

from models import Hopeful


def preporcess_login():
    if 'username' in session:
        return None
    return render_template('index.html')


@app.route("/")
def index():
    result = preporcess_login()
    if result is not None:
        return result
    return redirect(url_for('matches'))


@app.route("/matches")
def matches():
    result = preporcess_login()
    if result is not None:
        return result
    pynder_session = db_util.load_pynder_session(session['username'])
    current_matches = list(itertools.islice(
        pynder_session.matches(), 0, config['max_matches_shown']))

    matched_users = [x.user for x in current_matches]

    return render_template("matches.html", session=session, matched_users=matched_users)


@app.route("/swipe")
def swipe():
    pynder_session = db_util.load_pynder_session(session['username'])
    try:
        current_person = next(pynder_session.nearby_users())
    except Exception as e:
        return render_template("base.html", error="No people nearby. %s" % e)
    else:
        hopeful = Hopeful(current_person)
        db_util.add_hopeful(hopeful)
        return render_template("swipe.html", session=session, person=current_person, person_hash_code=hopeful.hash_code)


@app.route("/vote", methods=['POST'])
def vote():
    result = preporcess_login()
    if result is not None:
        return result
    hash_code = int(request.form['person_hash_code'])

    hopeful = db_util.get_hopeful(hash_code)
    vote = None

    for x in ["dislike", "like", "superlike"]:
        if x in request.form:
            vote = x

    print("voted: %s" % vote)

    if vote is None:
        print("Vote is None")
        return redirect(url_for('index'), error="vote was None")

    if vote == 'dislike':
        hopeful.dislike()
        match = False
    elif vote == 'like':
        match = hopeful.like()
    else:
        match = hopeful.superlike()

    print("match = %r" % match)

    if match is not False:
        message = "You have got a new match!"
        if match['is_super_like']:
            message += " %s superliked you :)" % hopeful.name

        flash(message)
        # return render_template('new_match.html', person=hopeful, match=match)
        return redirect(url_for('swipe'))
    else:
        return redirect(url_for('swipe'))


@app.route('/statistics')
def statistics():
    data = {
        'male': {
            'count': 0,
            'age': defaultdict(int),
            },
        'female': {
            'count': 0,
            'age': defaultdict(int),
            },
        'ages': []
    }

    hopefuls = list(db_util.get_all_hopefuls())

    for gender in ['male', 'female']:
        data[gender]['count'] = len(
            [x for x in hopefuls if x.gender == gender])

    for x in hopefuls:
        data[x.gender]['age'][x.age] += 1

    data['ages'] = [x for x in range(100) \
            if x in data['male']['age'] \
            or x in data['female']['age']]

    pretty_data = pformat(data, indent=2).replace("\n", "<br>")
    return render_template('statistics.html', data=data, pretty_data=pretty_data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']

            access_token = get_access_token(username, password)

            print("access token is %s" % access_token)

            if db_util.user_exists(username):
                print("user exists; updating access token")
                db_util.update_user(username, access_token)
            else:
                print("user does not exist; creating new")
                db_util.add_user(username, access_token)

            session['username'] = username
            # session['access_token'] = access_token

            return redirect(url_for('index'))

        except Exception as e:
            return render_template("base.html", error="Could not get access token. %s" % e)

    else:
        if 'username' in session:
            return redirect(url_for('index'))
        else:
            return render_template('login.html')


@app.route("/settings", methods=['GET', 'POST'])
def settings():
    pynder_session = db_util.load_pynder_session(session['username'])
    profile = Profile(pynder_session._api.profile(), pynder_session._api)
    form = SettingsForm(request.form)
    if request.method == 'POST' and form.validate():
        form.set_profile_from_fields(profile)
    else:
        pass
    form.set_fields_from_profile(profile)
    return render_template("settings.html", session=session, form=form)


@app.route('/logout')
def logout():
    result = preporcess_login()
    if result is not None:
        return result
    session.pop('username', None)
    # session.pop('access_token', None)
    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(error):
    return "page not found", 404
