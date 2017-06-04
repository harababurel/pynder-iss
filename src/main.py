#!/usr/bin/python3

import flask_sqlalchemy
import itertools
import pynder
import pickle

from flask import Flask, request, session, g, escape, render_template, abort, redirect, url_for
from flask_debugtoolbar import DebugToolbarExtension

from config import config

from PIL import Image

import re
import requests
import robobrowser


app = Flask(__name__)
app.debug = config['debug']
app.secret_key = config['secret_key']

toolbar = DebugToolbarExtension(app)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
from routes import *


# app.config['SOCIAL_FACEBOOK'] = {
#     # 'consumer_key': '1827578677482273',
#     'consumer_key': '464891386855067',
#     'consumer_secret': '2e7bba43653aba506d1f7e119857643b'
# }

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


def main():
    app.run()

if __name__ == '__main__':
    main()
