from flask import request, session, g, escape, render_template, abort, redirect, url_for, flash, jsonify
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

from models import Hopeful, TinderUser, Vote, Match
from statistics import generate_age_statistics


def logged_in():
    return 'username' in session


@app.route("/")
def index():
    if not logged_in():
        return render_template('index.html')
    return redirect(url_for('matches'))


@app.route("/chat/<id>", methods=['POST'])
def chat(id):
    pynder_session = db_util.load_pynder_session(session['username'])
    current_match = None
    for match in list(itertools.islice(
            pynder_session.matches(), 0, config['max_matches_shown'])):
        if match.user.id == id:
            current_match = match
    message = request.form['message']
    current_match.message(message)


@app.route("/matches")
def matches():
    if not logged_in():
        return render_template('index.html')
    pynder_session = db_util.load_pynder_session(session['username'])
    current_matches = list(itertools.islice(
        pynder_session.matches(), 0, config['max_matches_shown']))

    matched_users = [x.user for x in current_matches]

    return render_template("matches.html",
                           session=session,
                           matched_users=matched_users)


@app.route("/swipe")
def swipe():
    if not logged_in():
        return render_template('index.html')
    pynder_session = db_util.load_pynder_session(session['username'])
    try:
        current_person = next(pynder_session.nearby_users())
        db_util.add_tinder_user(TinderUser(current_person))
    except Exception as e:
        return render_template("base.html",
                               error="No people nearby. %s" % e)
    else:
        hopeful = Hopeful(current_person)
        db_util.add_hopeful(hopeful)
        return render_template("swipe.html",
                               session=session,
                               person=current_person,
                               person_hash_code=hopeful.hash_code)


@app.route("/vote", methods=['POST'])
def vote():
    if not logged_in():
        return render_template('index.html')

    pynder_session = db_util.load_pynder_session(session["username"])

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
        db_util.add(Match(pynder_session.profile.id, hopeful.id))
        message = "You have got a new match!"
        if match['is_super_like']:
            message += " %s superliked you :)" % hopeful.name

        flash(message)
        # return render_template('new_match.html', \
        #         person=hopeful, \
        #         match=match)
        return redirect(url_for('swipe'))
    else:
        return redirect(url_for('swipe'))


@app.route('/statistics')
@app.route('/statistics/<category>')
def statistics(category='general'):
    hopefuls = list(db_util.get_all_hopefuls())

    if category == 'general':
        data = generate_age_statistics(hopefuls)
        pretty_data = pformat(data, indent=2).replace("\n", "<br>")
        return render_template('statistics.html',
                               data=data,
                               pretty_data=pretty_data)

    else:
        data = None
        return "no personal statistics yet"


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

            pynder_session = db_util.load_pynder_session(username)
            db_util.add_tinder_user(TinderUser(pynder_session.profile))

            return redirect(url_for('index'))

        except Exception as e:
            return render_template("base.html",
                                   error="Could not get access token. %s" % e)

    else:
        if logged_in():
            return redirect(url_for('index'))
        else:
            return render_template('login.html')


@app.route("/settings", methods=['GET', 'POST'])
def settings():
    if not logged_in():
        return render_template('index.html')

    pynder_session = db_util.load_pynder_session(session['username'])

    form = SettingsForm(request.form)
    if request.method == 'POST' and form.validate():
        # data = dict([(a, getattr(form, a).data) for a in dir(
        #     form) if not a.startswith("__") and hasattr(getattr(form, a), 'data')])
        # pretty_data = pformat(data, indent=2).replace("\n", "<br>")
        # return pretty_data

        form.update_profile_from_fields(pynder_session)

    form.fill_fields_from_profile(pynder_session)

    return render_template("settings.html", session=session, form=form)


@app.route('/logout')
def logout():
    if not logged_in():
        return render_template('index.html')

    session.pop('username', None)
    # session.pop('access_token', None)
    return redirect(url_for('index'))


@app.route('/messages', methods=['POST'])
def messages():
    pynder_session = db_util.load_pynder_session(session['username'])
    current_match = None
    for match in list(itertools.islice(
            pynder_session.matches(), 0, config['max_matches_shown'])):
        if match.user.id == request.json['match']:
            current_match = match
    if current_match is not None:
        seen_messages = 0
        if not db_util.match_exists(pynder_session.profile.id, current_match.user.id):
            db_util.add(Match(pynder_session.profile.id, current_match.user.id))
        else:
            seen_messages = db_util.get_message_count(pynder_session.profile.id, current_match.user.id)
        messageList = current_match.messages
        if request.json['active']:
            if int(request.json['messageNumber']) == 0:
                return render_template("messages.html", messages=messageList, user=pynder_session.profile)
            if len(messageList) > seen_messages:
                messageList = messageList[int(request.json['messageNumber']):]
                db_util.set_message_count(pynder_session.profile.id, current_match.user.id, len(messageList))
                return render_template("messages.html", messages=messageList, user=pynder_session.profile)
        else:
            if len(messageList) > seen_messages:
                return jsonify("1")
    return ""


@app.route('/unmatch/<id>', methods=['POST'])
def unmatch(id):
    pynder_session = db_util.load_pynder_session(session['username'])
    current_match = None
    for match in list(itertools.islice(
            pynder_session.matches(), 0, config['max_matches_shown'])):
        if match.user.id == id:
            current_match = match
    current_match.delete()


@app.errorhandler(404)
def page_not_found(error):
    return "page not found", 404
