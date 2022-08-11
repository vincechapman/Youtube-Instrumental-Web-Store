from flask import Flask, request

worker = Flask(__name__)

@worker.route('/', method=['POST'])
def worker():

    print('Job was queued')
    print(request.values)
