from flask import Flask, request, jsonify

print('This file has been read.')

worker = Flask(__name__)

@worker.route('/', methods=['POST'])
def task_handler():

    print('Job was queued')

    print('\nData:')
    print(request.data)
    
    print('\nValues:')
    print(request.values)

    print('\nGet Data:')
    print(request.get_data(as_text=True))

    print('\nGet json:')
    print(request.get_json())

    resp = jsonify(success=True)
    return resp
