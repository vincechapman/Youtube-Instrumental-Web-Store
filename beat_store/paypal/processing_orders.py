import os
from dotenv import load_dotenv
load_dotenv()

from flask import redirect, url_for, request, render_template

from . import bp, client

from .. paypalcheckoutsdk.orders import OrdersCreateRequest, OrdersCaptureRequest, OrdersGetRequest
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



@bp.route('/confirming', methods=['GET', 'POST'])
def capture_order():

    if request.method == 'POST':

        artists_legal_name = request.form['artists_legal_name']
        artists_professional_name = request.form['artists_professional_name']

        url = request.url
        order_id = [i.split('=') for i in url[url.find('?') + 1:].split('&')][0][1]

        try:

            capture_request = OrdersCaptureRequest(order_id) # This should be an Approved Order ID
            response = client.execute(capture_request)

            amount_paid = response.result.purchase_units[0]['payments']['captures'][0]['amount']['value']

            currency_code = response.result.purchase_units[0]['payments']['captures'][0]['amount']['currency_code']
            if currency_code == 'GBP':
                currency_code = '£'
            else:
                currency_code += ' '

            video_id = response.result.purchase_units[0]['payments']['captures'][0]['custom_id']
            # video = Videos.query.get(video_id)

            # lease_id = create_lease(
            #     producers_legal_name='Vincent Chapman-Andrews', # Update Model so that I get added by default, and then if any featured artists are specified they get added too.
            #     producers_professional_name='Vince Maina',
            #     artists_legal_name=artists_legal_name,
            #     artists_professional_name=artists_professional_name,
            #     beat_name=video.video_beat_name,
            #     youtube_link=f'https://youtu.be/{video_id}', # FIX
            #     composer_legal_name='Vincent Chapman-Andrews',
            #     beat_price= currency_code + amount_paid, # FIX - SHOULD MATCH WHAT IS IN THE PAYPAL ORDER RECIEPT.
            #     order_id=order_id
            # )

            # send_confirmation_email(
            #     order_id = order_id,
            #     beat_name = video.video_beat_name,
            #     video_title = video.video_title,
            #     recipient_address = 'vince@elevatecopy.com', # UPDATE THIS TO USE ACTUAL ADDRESS FROM PAYPAL ORDER
            #     lease_id = lease_id
            # )

            lease_id='test'

            return redirect(url_for('paypal.receipt', order_id=order_id, lease_id=lease_id))

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

    return render_template('lease_form.html')


@bp.route('/<order_id>/<lease_id>/receipt', methods=['GET', 'POST'])
def receipt(order_id, lease_id):

    request = OrdersGetRequest(order_id)
    response = client.execute(request)

    video_id = response.result.purchase_units[0]['custom_id']

    return 'reached reciept page'
        
    # video = Videos.query.get(video_id)
    # video_beat_name = video.video_beat_name

    # stems, mixdowns = fetch_beat_files(video_beat_name)

    # from drive import return_links
    # link_for_stems, link_for_mixdown = return_links(video_beat_name) 

    # from flask import request

    # if request.method == 'POST':
    #     # if request.form['submit'] == 'mixdowns':
    #     #     return download_all_files(video_beat_name, mixdowns, 'mixdowns')
    #     # elif request.form['submit'] == 'stems':
    #     #     return download_all_files(video_beat_name, stems, 'stems')
    #     if request.form['submit'] == 'lease':
    #         return export_lease(lease_id, f'Licence - {video_beat_name} ({order_id}).pdf')
    # else:
    #     return render_template('receipt.html', order_id=order_id, video=video, stems=stems, mixdowns=mixdowns, link_for_stems=link_for_stems, link_for_mixdown=link_for_mixdown)

