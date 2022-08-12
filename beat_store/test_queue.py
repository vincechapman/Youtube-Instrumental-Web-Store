'''
This page allows me to send messages to my queue, and then we can check our worker environment logs to see if those messages were received.
If successful, we can check if we're able to use those messages to trigger functions (using conditional statements)
'''

from flask import Blueprint, request

bp = Blueprint('test_queue', __name__, url_prefix='/queue')


@bp.route('/send_request', methods=['GET', 'POST'])
def send_request():

    message_id = 'Send a message first.'

    from rq import Queue
    from . worker import conn

    queue = Queue('default', connection=conn)

    if request.method == 'POST':

        count_to = int(request.form['message'])
        

        from . import test_function

        job = queue.enqueue(test_function, count_to)

        message_id = job
        

    return f'''
        <h1>Send a message to SQS queue</h1>

        <form action="#" method="post">
            <input type="number" name="message" required>
            <input type="submit" value="submit">
        </form>

        <div>ID of last message: {message_id}</div>
        
        <div>Job queue:</div>
        {queue.jobs}

        '''
