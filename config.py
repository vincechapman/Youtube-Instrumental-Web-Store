from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

import os
from dotenv import load_dotenv
load_dotenv()

from rq import Queue
from worker import conn
q = Queue(connection=conn)

'''----------------------------------------------------------------------------------------------------
IMPORTING ENVIRONMENT VARIABLES'''

BEAT_WEBSITE_OAUTH_CREDENTIALS = os.environ.get('BEAT_WEBSITE_OAUTH_CREDENTIALS')
PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_SANDBOX_CLIENT_ID')
PAYPAL_CLIENT_SECRET = os.environ.get('PAYPAL_SANDBOX_CLIENT_SECRET')
PAYPAL_LIVE = (os.environ.get('PAYPAL_LIVE')).lower()
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
TOKEN_JSON = os.environ.get('TOKEN_JSON')

DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

'''----------------------------------------------------------------------------------------------------
CONFIG'''

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

wsgi_app = app.wsgi_app

def get_domain():
    domain = request.root_url[:-1]
    return domain

'''----------------------------------------------------------------------------------------------------
WEBSITE VARIABLES'''

lease_price = '35.00' # Use a text file or something to store the lease price.

sender_address = 'vchapandrews@gmail.com'