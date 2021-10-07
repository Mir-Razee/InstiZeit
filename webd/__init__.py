from flask import Flask
from authlib.integrations.flask_client import OAuth
import os
from datetime import timedelta
from webd import decorator

app = Flask(__name__)

# from dotenv import load_dotenv
# load_dotenv()

# Session config
app.secret_key = 'super-secret-key'
app.config['SESSION_COOKIE_NAME'] = 'google-login-session'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)

# oAuth Setup
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id='220667430071-j0aoshm8dstq6fvluqtrfiirnl59o6a9.apps.googleusercontent.com',
    client_secret='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',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',  # This is only needed if using openId to fetch user info
    client_kwargs={'scope': 'openid email profile'},
)

from webd import routes

