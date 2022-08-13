from flask import Blueprint, render_template, request

bp = Blueprint('test_cron', __name__, url_prefix='/cron')


@bp.route('/test-cron', methods=['GET', 'POST'])
def update_database():
    
    if request.method == 'POST':

        from . mail import send_confirmation_email

        response = send_confirmation_email('012345TEST', 'TESTBEATNAME', 'TESTVIDEOTITLE', 'vince@elevatecopy.com', '1Eny9AaVXVbFvAljb2rD47pP6exeuzvPgoeW5gep-0BY')

        return f'Email sent: {response}'

    return '''
        <h1>Cron Scheduling Test</h1>

        <form action="#" method="post">
            <input type="submit" value="submit">
        </form>
        '''
