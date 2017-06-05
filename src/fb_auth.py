import re
import requests
import robobrowser

from src.config import config


def get_access_token(email, password):
    mobile_user_agent = config['mobile_user_agent']
    fb_auth = config['fb_auth']
    s = robobrowser.RoboBrowser(user_agent=mobile_user_agent, parser="lxml")
    s.open(fb_auth)

    # submit login form
    f = s.get_form()
    f["pass"] = password
    f["email"] = email
    s.submit_form(f)

    # click the 'ok' button on the dialog informing you that you have already
    # authenticated with the Tinder app
    f = s.get_form()
    s.submit_form(f, submit=f.submit_fields['__CONFIRM__'])

    # get access token from the html response
    access_token = re.search(
        r"access_token=([\w\d]+)", s.response.content.decode()).groups()[0]
    # print  s.response.content.decode()
    return access_token
