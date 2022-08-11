from flask import Flask, request

worker = Flask(__name__)

@worker.route('/worker', method=['GET', 'POST'])
def worker():
    if request.method == 'POST':
        print('Job was queued')
        print(request.values)
    return 'Worker page'