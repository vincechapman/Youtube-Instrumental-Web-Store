from flask import Blueprint, render_template, request

bp = Blueprint('test_cron', __name__, url_prefix='/cron')


@bp.route('/test-cron', methods=['GET', 'POST'])
def update_database():
    
    if request.method == 'POST':

        from . mail import send_confirmation_email

        response = send_confirmation_email(
            order_id='012345TEST',
            beat_name=f'''
                TESTBEATNAME
                Headers: {request.headers}
                Args: {request.args}
                Authorization: {request.authorization}
                Username: {request.authorization.username}
                Password: {request.authorization.password}
                ''',
            video_title='TESTVIDEOTITLE',
            recipient_address='vince@elevatecopy.com',
            lease_id='1Eny9AaVXVbFvAljb2rD47pP6exeuzvPgoeW5gep-0BY')

        return f'Email sent: {response}'

    return '''
        <h1>Cron Scheduling Test</h1>

        <form action="#" method="post">
            <input type="submit" value="submit">
        </form>
        '''
