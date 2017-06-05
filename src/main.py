#!/usr/bin/python3

import flask_sqlalchemy

from flask import Flask
from flask_login import login_required, login_user, logout_user, current_user
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy

from src.config import config

app = Flask(__name__)
app.debug = config['debug']
app.secret_key = config['secret_key']

toolbar = DebugToolbarExtension(app)

for app_setting in config['app'].items():
    app.config[app_setting[0]] = app_setting[1]

db = SQLAlchemy(app)

from src.db_util import *
from src.routes import *
from src.models import User


def main():
    try:
        db.create_all()
    except:
        print("could not create database. maybe it already exists?")
    app.run(host='0.0.0.0', port=config['port'])

if __name__ == '__main__':
    main()
