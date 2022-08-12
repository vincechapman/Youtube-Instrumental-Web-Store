from flask import Flask, request

application = Flask(__name__)

@application.route('/', methods=['POST'])
def task_handler():

    print('Job was queued')
    print(request.values)
