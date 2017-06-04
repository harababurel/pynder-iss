#!/usr/bin/python3

import flask_sqlalchemy
import itertools
import pynder
import pickle

from flask import Flask, request, session, g, escape, render_template, abort, redirect, url_for
from flask_login import login_required, login_user, logout_user, current_user
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy

from config import config

from PIL import Image

import re
import requests
import robobrowser
import os.path

app = Flask(__name__)
app.debug = config['debug']
app.secret_key = config['secret_key']

toolbar = DebugToolbarExtension(app)

for app_setting in config['app'].items():
    app.config[app_setting[0]] = app_setting[1]

db = SQLAlchemy(app)

from routes import *
from models import *


def get_access_token(email, password):
    mobile_user_agent = config['mobile_user_agent']
    fb_auth = config['fb_auth']
    s = robobrowser.RoboBrowser(user_agent=mobile_user_agent, parser="lxml")
    s.open(fb_auth)
    ##submit login form##
    f = s.get_form()
    f["pass"] = password
    f["email"] = email
    s.submit_form(f)
    # click the 'ok' button on the dialog informing you that you have already
    # authenticated with the Tinder app##
    f = s.get_form()
    s.submit_form(f, submit=f.submit_fields['__CONFIRM__'])
    ##get access token from the html response##

    access_token = re.search(
        r"access_token=([\w\d]+)", s.response.content.decode()).groups()[0]
    # print  s.response.content.decode()
    return access_token


def create_pynder_session(FBTOKEN, FBID=None):
    session = pynder.Session(facebook_id=FBID, facebook_token=FBTOKEN)
    return session


def dump_pynder_session_to_file(access_token):
    try:
        with open('sessions/%s' % access_token, 'wb') as f:
            pickle.dump(create_pynder_session(access_token), f)
            print("dumped session to file")
    except Exception as e:
        print("could not dump pynder session to file. reason:\n%s" % e)


def load_pynder_session(access_token):
    pynder_session = None
    filename = "sessions/%s" % access_token

    if not os.path.isfile(filename):
        try:
            print("session doesn't exist. trying to create a new one")
            dump_pynder_session_to_file(access_token)
        except Exception as e:
            print("could not create new session. reason:\n%s" % e)

    try:
        print("loading session from file")
        with open('sessions/%s' % access_token, 'rb') as f:
            pynder_session = pickle.load(f)
    except Exception as e:
        print("could not load session from file. reason:\n%s" % e)

    return pynder_session


def main():
    try:
        db.create_all()
    except:
        print("could not create database. maybe it already exists?")
    app.run(host='0.0.0.0', port=config['port'])

if __name__ == '__main__':
    main()
