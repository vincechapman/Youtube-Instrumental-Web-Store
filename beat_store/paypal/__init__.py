from .. paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment, LiveEnvironment
from paypalhttp import HttpError

import os
from dotenv import load_dotenv
load_dotenv()

# PAYPAL_LIVE = os.environ['PAYPAL_LIVE']
PAYPAL_LIVE = False
PAYPAL_CLIENT_ID = os.environ['PAYPAL_CLIENT_ID']
PAYPAL_CLIENT_SECRET = os.environ['PAYPAL_CLIENT_SECRET']

if PAYPAL_LIVE.lower() == 'true':
    environment = LiveEnvironment(
        client_id=PAYPAL_CLIENT_ID,
        client_secret=PAYPAL_CLIENT_SECRET
        )
elif PAYPAL_LIVE.lower() == 'false':
    environment = SandboxEnvironment(
        client_id=PAYPAL_CLIENT_ID,
        client_secret=PAYPAL_CLIENT_SECRET
        )
client = PayPalHttpClient(environment)

from flask import Blueprint

bp = Blueprint('paypal', __name__, url_prefix='/order')