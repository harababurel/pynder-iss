from main import *


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
    current_matches = list(itertools.islice(
        pynder_session.matches(), 0, config['max_matches_shown']))

    matched_users = [x.user for x in current_matches]

    return render_template("matches.html", session=session, matched_users=matched_users)


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
