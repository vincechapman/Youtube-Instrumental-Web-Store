from flask import Flask, request

app = Flask(__name__)

@app.route('/worker', method=['GET', 'POST'])
def worker():
    if request.method == 'POST':
        print('Job was queued')
        print(request.values)