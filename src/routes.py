from flask import request, session, g, escape, render_template, abort, redirect, url_for
from pynder.models import Profile

from form_util import SettingsForm
from main import app
from config import config
from fb_auth import get_access_token
import itertools
import db_util


@app.route("/")
def index():
    if 'username' in session:

        return redirect(url_for('matches'))
    else:
        return render_template('index.html')


@app.route("/matches")
def matches():
    pynder_session = db_util.load_pynder_session(session['username'])
    current_matches = list(itertools.islice(
        pynder_session.matches(), 0, config['max_matches_shown']))

    matched_users = [x.user for x in current_matches]

    return render_template("matches.html", session=session, matched_users=matched_users)


@app.route("/swipe")
def swipe():
    pynder_session = db_util.load_pynder_session(session['username'])
    current_person = next(pynder_session.nearby_users())

    return render_template("swipe.html", session=session, person=current_person)


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
                db_util.create_user(username, access_token)

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
    session.pop('username', None)
    # session.pop('access_token', None)
    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(error):
    return "page not found", 404
