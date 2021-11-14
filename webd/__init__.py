from flask import Flask
from authlib.integrations.flask_client import OAuth
import os
from datetime import timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import datetime
import sys
application = Flask(__name__)

from dotenv import load_dotenv
load_dotenv()

UPLOAD_FOLDER = 'media'
# Session config
application.secret_key = 'super-secret-key'
application.config['SESSION_COOKIE_NAME'] = 'google-login-session'
application.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15)
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# oAuth Setup
oauth = OAuth(application)
google = oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_PASSWORD"),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',  # This is only needed if using openId to fetch user info
    client_kwargs={'scope': 'openid email profile'},
)

DATABASE_PASSWORD=os.getenv("DATABASE_PASSWORD")
engine = create_engine(DATABASE_PASSWORD)

try:
    conn = engine.connect()
except Exception as e:
    print('Connection Failed\nError Details:', e)
    sys.exit(1)
conn.close()

db = scoped_session(sessionmaker(bind=engine))


from webd import msg

from webd import routes

