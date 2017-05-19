#!/usr/bin/python3

import itertools
import pynder
import pickle

from flask import Flask, request, session, g, escape, render_template, abort, redirect, url_for
from flask_debugtoolbar import DebugToolbarExtension

from PIL import Image

import re
import requests
import robobrowser
import urllib.request
import shutil
import os.path
import getpass

from subprocess import call


app = Flask(__name__)
app.debug = True

app.secret_key = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
toolbar = DebugToolbarExtension(app)

PHOTO_DIR = 'tmp/'
SHOWN_MATCHES = 100

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

app.config['SOCIAL_FACEBOOK'] = {
    # 'consumer_key': '1827578677482273',
    'consumer_key': '464891386855067',
    'consumer_secret': '2e7bba43653aba506d1f7e119857643b'
}


def get_access_token(email, password):
    MOBILE_USER_AGENT = "Mozilla/5.0 (Linux; U; en-gb; KFTHWI Build/JDQ39) AppleWebKit/535.19 (KHTML, like Gecko) Silk/3.16 Safari/535.19"
    FB_AUTH = "https://www.facebook.com/v2.6/dialog/oauth?redirect_uri=fb464891386855067%3A%2F%2Fauthorize%2F&display=touch&state=%7B%22challenge%22%3A%22IUUkEUqIGud332lfu%252BMJhxL4Wlc%253D%22%2C%220_auth_logger_id%22%3A%2230F06532-A1B9-4B10-BB28-B29956C71AB1%22%2C%22com.facebook.sdk_client_state%22%3Atrue%2C%223_method%22%3A%22sfvc_auth%22%7D&scope=user_birthday%2Cuser_photos%2Cuser_education_history%2Cemail%2Cuser_relationship_details%2Cuser_friends%2Cuser_work_history%2Cuser_likes&response_type=token%2Csigned_request&default_audience=friends&return_scopes=true&auth_type=rerequest&client_id=464891386855067&ret=login&sdk=ios&logger_id=30F06532-A1B9-4B10-BB28-B29956C71AB1&ext=1470840777&hash=AeZqkIcf-NEW6vBd"
    s = robobrowser.RoboBrowser(user_agent=MOBILE_USER_AGENT, parser="lxml")
    s.open(FB_AUTH)
    ##submit login form##
    f = s.get_form()
    f["pass"] = password
    f["email"] = email
    s.submit_form(f)
    ##click the 'ok' button on the dialog informing you that you have already authenticated with the Tinder app##
    f = s.get_form()
    s.submit_form(f, submit=f.submit_fields['__CONFIRM__'])
    ##get access token from the html response##

    access_token = re.search(r"access_token=([\w\d]+)", s.response.content.decode()).groups()[0]
    #print  s.response.content.decode()
    return access_token

def create_pynder_session(FBTOKEN, FBID=None):
    session = pynder.Session(facebook_id=FBID, facebook_token=FBTOKEN)
    return session


@app.route("/")
def index():
    if 'username' in session:
        return redirect(url_for('matches'))
    else:
        return render_template('index.html')
        # return redirect(url_for('login'))

@app.route("/matches")
def matches():
    pynder_session = load_pynder_session(session['access_token'])
    current_matches = list(itertools.islice(pynder_session.matches(), 0, SHOWN_MATCHES))

    matched_users = [x.user for x in current_matches]

    return render_template("matches.html", session=session, matched_users=matched_users)


def dump_pynder_session_to_file(access_token):
    with open('sessions/%s' % access_token, 'wb') as g:
        pickle.dump(create_pynder_session(access_token), g)
        print("dumped session to file")

def load_pynder_session(access_token):
    try:
        with open('sessions/%s' % access_token, 'rb') as f:
            pynder_session = pickle.load(f)
    except:
        dump_pynder_session_to_file(access_token)
        with open('sessions/%s' % access_token, 'rb') as f:
            pynder_session = pickle.load(f)

    return pynder_session


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']

            access_token = get_access_token(username, password)

            session['username'] = username
            session['access_token'] = access_token

            return redirect(url_for('index'))

        except Exception as e:
            return render_template("base.html", error="Could not get access token. %s" % e)
    else:
        if 'username' in session:
            return redirect(url_for('index'))
        else:
            return render_template('login.html')

@app.route('/fb')
def fb():
    return render_template('fb.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(error):
    return "page not found", 404

def main():
    app.run()

if __name__=='__main__':
    main()
