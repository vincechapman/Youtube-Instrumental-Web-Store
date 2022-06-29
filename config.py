from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()

'''----------------------------------------------------------------------------------------------------
IMPORTING ENVIRONMENT VARIABLES'''

BEAT_WEBSITE_OAUTH_CREDENTIALS = os.environ.get('BEAT_WEBSITE_OAUTH_CREDENTIALS')
PAYPAL_SANDBOX_CLIENT_ID = os.environ.get('PAYPAL_SANDBOX_CLIENT_ID')
PAYPAL_SANDBOX_CLIENT_SECRET = os.environ.get('PAYPAL_SANDBOX_CLIENT_SECRET')
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
TOKEN_JSON = os.environ.get('TOKEN_JSON')

'''----------------------------------------------------------------------------------------------------
CONFIG'''

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
wsgi_app = app.wsgi_app

def get_domain():
    domain = request.root_url[:-1]
    return domain

lease_price = '30.00' # Use a text file or something to store the lease price.

sender_address = 'vchapandrews@gmail.com'