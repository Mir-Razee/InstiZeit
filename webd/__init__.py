from flask import Flask
from authlib.integrations.flask_client import OAuth
import os
from datetime import timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from imgurpython import ImgurClient
from datetime import datetime

app = Flask(__name__)

from dotenv import load_dotenv
load_dotenv()

UPLOAD_FOLDER = 'D:\\imgur'
# Session config
app.secret_key = 'super-secret-key'
app.config['SESSION_COOKIE_NAME'] = 'google-login-session'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

DATABASE_PASSWORD=os.getenv("DATABASE_PASSWORD")
engine = create_engine(DATABASE_PASSWORD)

try:
    conn = engine.connect()
except Exception as e:
    print('Connection Failed\nError Details:', e)
    sys.exit(1)
conn.close()

db = scoped_session(sessionmaker(bind=engine))

client_id = '95794ccc4e8dd31'
client_secret = '62b526f23e2c6c55c9c816c0cbd99be61753598a'

client = ImgurClient(client_id, client_secret)

print(client)

from webd import routes

