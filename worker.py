from flask import Flask, request

print('This file has been read.')

worker = Flask(__name__)

@worker.route('/', methods=['POST'])
def task_handler():

    print('Job was queued')
    print(request.values)

    return 'Job was queued - return'
