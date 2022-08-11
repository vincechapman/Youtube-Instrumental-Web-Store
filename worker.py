from flask import Flask, request

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

    return 200
