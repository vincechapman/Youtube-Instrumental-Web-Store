'''
This page allows me to send messages to my queue, and then we can check our worker environment logs to see if those messages were received.
If successful, we can check if we're able to use those messages to trigger functions (using conditional statements)
'''

from flask import Blueprint, render_template, request

bp = Blueprint('test_queue', __name__, url_prefix='/queue')


def pickle(obj):

    import codecs
    import pickle

    pickled = codecs.encode(pickle.dumps(obj), "base64").decode()
    
    return pickled


def queue_function(queue, message, *args, **kwargs):

    args = pickle(args)
    kwargs = pickle(kwargs)

    response = queue.send_message(
        MessageBody=message,
        MessageAttributes={
            'args': {
                'StringValue': args,
                'DataType': 'String'},
            'kwargs': {
                'StringValue': kwargs,
                'DataType': 'String'}})

    return response


@bp.route('/send_request', methods=['GET', 'POST'])
def send_request():

    message_id = 'Send a message first.'

    if request.method == 'POST':

        import os
        from dotenv import load_dotenv
        load_dotenv()

        import boto3

        from botocore.exceptions import ClientError

        sqs = boto3.resource('sqs')

        try:
            queue = sqs.get_queue_by_name(QueueName=os.environ['AWS_SQS_QUEUE_NAME'])
        except ClientError as e:
            raise Exception(f'{e}\n\nHint: Add the name of an existing to queue to environment variables with the key AWS_SQS_QUEUE_NAME')

        message = request.form['message']

        message_id = queue_function(queue, message)

    return f'''
        <h1>Send a message to SQS queue</h1>

        <form action="#" method="post">
            <input type="text" name="message">
            <input type="submit" value="submit">
        </form>

        ID of last message: {message_id}
        '''
