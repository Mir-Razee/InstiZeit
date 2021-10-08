from webd import app
from flask import redirect, url_for, session, render_template
from webd import oauth

@app.route("/")
def landing():
    user = dict(session).get('profile', None)
    if user:
        return render_template('home.html',user=user)
    else:
        return render_template('landing.html')

@app.route('/login')
def login():
    google = oauth.create_client('google')  # create the google oauth client
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')  # create the google oauth client
    token = google.authorize_access_token()  # Access token from google (needed to get user info)
    resp = google.get('userinfo')  # userinfo contains stuff u specificed in the scrope
    user_info = resp.json()
    user = oauth.google.userinfo()  # uses openid endpoint to fetch user info
    # Here you use the profile/user data that you got and query your database find/register the user
    # and set ur own data in the session not the profile from google
    session['profile'] = user_info
    session.permanent = True  # make the session permanant so it keeps existing after browser gets closed
    return redirect('/')

@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')
