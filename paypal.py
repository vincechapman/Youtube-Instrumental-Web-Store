from __future__ import print_function

import json

from datetime import datetime
from random import randint

from flask import redirect, render_template, url_for, request
from flask_sqlalchemy import SQLAlchemy
from googleapiclient.discovery import build
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment
from paypalcheckoutsdk.orders import (OrdersCaptureRequest,
                                      OrdersCreateRequest, OrdersGetRequest)
from paypalhttp import HttpError

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

'''-------------------------------------------------------------------'''

from config import app, live_address, local_address, lease_price
from models import Videos
from drive import fetch_beat_files, download_all_files

'''--------------------------------------------------------------------------'''

domain = live_address
if __name__ == '__main__':
    domain = local_address

'''-------------------------------------------------------------------------------------------------------------------
PAYPAL API - ACCEPTING PAYMENTS'''

# Creating an environment
environment = SandboxEnvironment(
    client_id="AS1132c74w5Psl0sERRvJe2WzccSgsbG-OgU1XRQ9DmoYE2cCz9vWhDG6QGI_yADG0ZnKlSdU-UrOTSw", # DOES THIS NEED TO BE CONCEALED? (MAYBE USING ENVIRONEMENT VARIABLES)
    client_secret="EChc2bGK8cRIxZov3_nLNvbAcpwyqO7r812LHIWX76Qw_WKmaKBdvCuVaWt9nczGmORPjgHJXHtohl2s" # DOES THIS NEED TO BE CONCEALED? (MAYBE USING ENVIRONEMENT VARIABLES)
    )
client = PayPalHttpClient(environment)

@app.route('/beats/<video_id>/<video_title>/purchase')
def create_order(video_id, video_title):

    reference_id = str(datetime.utcnow()) + str(randint(0,1000))

    request = OrdersCreateRequest()

    request.prefer('return=representation')

    request.request_body (
        {
            'intent' : 'CAPTURE',
            'purchase_units': [
                {
                    'description': video_title, # CHANGE THIS TO YOUTUBE VIDEO TITLE
                    'custom_id': video_id, # CHANGE THIS TO YOUTUBE VIDEO ID
                    'reference_id': reference_id,
                    'soft_descriptor': 'Vince Maina', # THIS IS WHAT SHOWS IN BANK STATEMENT: 'PAYPAL *Vince Maina'
                    'amount': {
                        'currency_code': 'GBP',
                        'value': lease_price
                    }
                }
            ],
            'application_context': {
                'brand_name': 'Vince Maina',
                'cancel_url': domain + '/beats/' + video_id, # FIX THIS
                'return_url': domain + '/confirming', # Basically this should forward the user to a payment confirmation page where they can access their files and lease document.
                'user_action': 'PAY_NOW'
            }
        }
    )

    # Executes request
    try:
        response = client.execute(request)

        print('Status Code:', response.status_code)
        print(json.dumps(response.result.dict(), indent = 4))

        order_id = response.result.id
        print('\nOrder ID:', order_id, '\n')

        # Fetches approval link. Have used this approach in case the approval link is not the second link returned.
        if response.result.links[1]['rel'] == 'approve':
            approve_link = response.result.links[1]['href']
        else:
            print('False') # Add for loop here to iterate through all links until it finds the approve link.

        # CUSTOMER APPROVES TRANSACTION
        return redirect(approve_link)

    except IOError as ioe:
        print('EXCEPTION\n', ioe)
        if isinstance(ioe, HttpError):
            # Something went wrong server-side
            print(ioe.status_code)

@app.route('/confirming')
def capture_order():

    from flask import \
        request  # Check if there's a way I can do this without having to import this package here inside the function
    url = request.url

    order_id = [i.split('=') for i in url[url.find('?') + 1:].split('&')][0][1]

    request = OrdersCaptureRequest(order_id) # This should be an Approved Order ID

    try:
        response = client.execute(request)
        print(json.dumps(response.result.dict(), indent = 4))

        return redirect(url_for('receipt', order_id=order_id))

    except IOError as ioe:
        if isinstance(ioe, HttpError):
            # Something went wrong server-side i.e. Paypal's end
            print(ioe.status_code)
            print(ioe.headers)
            print(ioe)
        else:
            # Something went wrong client side
            print(ioe)

        return redirect(url_for('error_payment_not_captured'))

@app.route('/<order_id>/receipt', methods=['GET', 'POST'])
def receipt(order_id):

    request = OrdersGetRequest(order_id)
    response = client.execute(request)

    # mail.send_email() 

    print('\n\n\nGET REQEUEST:')
    print(json.dumps(response.result.dict(), indent = 4))

    video_id = response.result.purchase_units[0]['custom_id']
        
    video = Videos.query.get(video_id)
    video_beat_name = video.video_beat_name # SLICED because saved as string with dictionary syntax i.e. '['Beat_name']'

    stems, mixdowns = fetch_beat_files(video_beat_name)

    from flask import request

    if request.method == 'POST':
        if request.form['submit'] == 'mixdowns':
            return download_all_files(video_beat_name, mixdowns, 'mixdowns')
        else:
            return download_all_files(video_beat_name, stems, 'stems') # FIX 
    else:

        return render_template('receipt.html', order_id=order_id, video=video, stems=stems, mixdowns=mixdowns)

