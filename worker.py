from flask import Flask, request

worker = Flask(__name__)

@worker.route('/', methods=['POST'])
def task_handler():

    print('Job was queued')
    print(request.values)
