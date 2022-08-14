import os
from dotenv import load_dotenv
load_dotenv()

from flask import redirect, url_for, request, render_template, current_app

from . import bp, client

from . paypalcheckoutsdk.orders import OrdersCreateRequest, OrdersCaptureRequest, OrdersGetRequest
from paypalhttp import HttpError

@bp.route('/<video_id>/<video_title>/purchase')
def create_order(video_id, video_title):

    from datetime import datetime
    from random import randint

    from .. import get_domain

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
                        'value': os.environ['STANDARD_LEASE_PRICE']
                    }
                }
            ],
            'application_context': {
                'brand_name': 'Vince Maina',
                'cancel_url': get_domain() + url_for('beats.beat', video_id=video_id),
                'return_url': get_domain() + url_for('paypal.capture_order'),
                'user_action': 'PAY_NOW'
            }
        }
    )

    # Executes request
    try:
        response = client.execute(request)

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


@bp.route('/confirming')
def capture_order():

    url = request.url
    order_id = [i.split('=') for i in url[url.find('?') + 1:].split('&')][0][1]

    try:

        capture_request = OrdersCaptureRequest(order_id) # This should be an Approved Order ID
        response = client.execute(capture_request)

        import json
        print('Capture order:\n', json.dumps(response.result.dict(), indent = 4))

        amount_paid = response.result.purchase_units[0]['payments']['captures'][0]['amount']['value']

        # Payer details
        given_name = response.result.payer.name.given_name
        surname = response.result.payer.name.surname
        full_name = ' '.join([given_name, surname])
        email_address = response.result.payer.email_address
        payer_id = response.result.payer.payer_id

        print(f'Given name: {given_name}')
        print(f'surname: {surname}')
        print(f'Full name: {full_name}')
        print(f'email address: {email_address}')
        print(f'payer_id: {payer_id}')

        currency_code = response.result.purchase_units[0]['payments']['captures'][0]['amount']['currency_code']
        if currency_code == 'GBP':
            currency_code = '£'
        else:
            currency_code += ' '

        video_id = response.result.purchase_units[0]['payments']['captures'][0]['custom_id']

        from .. db import get_db

        with current_app.app_context():

            db = get_db()
            cursor = db.cursor()

            data = cursor.execute('SELECT title, beat_name FROM video WHERE id = ?', (video_id,)).fetchone()
            title, beat_name = data

        from .. google_api.docs import create_lease

        lease_id = create_lease(
            producers_legal_name='Vincent Chapman-Andrews', # Update Model so that I get added by default, and then if any featured artists are specified they get added too.
            producers_professional_name='Vince Maina',
            beat_name=beat_name,
            youtube_link=f'https://youtu.be/{video_id}',
            composer_legal_name='Vincent Chapman-Andrews',
            beat_price= currency_code + amount_paid,
            order_id=order_id,
            payer_account_id=payer_id,
            payer_email=email_address,
            payer_name=full_name
        )

        # Sends the customer a confirmation email

        from .. google_api.mail import send_confirmation_email
        send_confirmation_email(
            order_id = order_id,
            beat_name = beat_name,
            video_title = title,
            recipient_address = 'vince@elevatecopy.com', # UPDATE THIS TO USE ACTUAL ADDRESS FROM PAYPAL ORDER
            lease_id = lease_id
        )

        return redirect(url_for('receipt.receipt', order_id=order_id, lease_id=lease_id))

    except IOError as ioe:
        if isinstance(ioe, HttpError):
            # Something went wrong server-side i.e. Paypal's end
            print('Something went wrong on Paypal\'s end.')
            print(ioe.status_code)
            print(ioe.headers)
            print(ioe)
            return 'Error 001: Payment error. Please contact site owner.'
        else:
            # Something went wrong client side
            print('Something went wrong client side')
            print(ioe)
            return "Form already completed. The link to get back to the receipt page is included in the purchase confirmation email."
