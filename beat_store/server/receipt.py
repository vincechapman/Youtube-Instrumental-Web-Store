from flask import current_app, Blueprint, render_template

from .. paypal.paypalcheckoutsdk.orders import OrdersGetRequest
from .. paypal import client

bp = Blueprint('receipt', __name__)

@bp.route('/receipt/<order_id>/<lease_id>', methods=['GET', 'POST'])
def receipt(order_id, lease_id):

    request = OrdersGetRequest(order_id)
    response = client.execute(request)

    video_id = response.result.purchase_units[0]['custom_id']

    from .. db import get_db
    with current_app.app_context():
        
        db = get_db()
        cursor = db.cursor()

        data = cursor.execute("SELECT * FROM video WHERE id = ?", (video_id,)).fetchone()
        id, title, published_at, thumbnail, description, beat_name, tags, link_to_mixdown, link_to_stems, link_to_video_audio = data

        print('\n\n')
        print(f'\nID: {id}')
        print(f'\nTITLE: {title}')
        print(f'\nPUBLISHED: {published_at}')
        print(f'\nTHUMBNAIL: {thumbnail}')
        print(f'\nDESCRIPTION: {description}')
        print(f'\nBEAT NAME: {beat_name}')
        print(f'\nTAGS: {tags}')
        print(f'\nLINK TO MIXDOWN: {link_to_mixdown}')
        print(f'\nLINK TO STEMS: {link_to_stems}')
        print(f'\nLINK TO AUDIO: {link_to_video_audio}')
        print('\n\n')

    from flask import request

    return render_template('receipt.html', order_id=order_id, link_to_stems=link_to_stems, link_to_mixdown=link_to_mixdown, beat_name=beat_name, title=title, id=id)
