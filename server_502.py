from flask import Flask
import time

app = Flask(__name__)

@app.route('/index')
def get():
    return '<h1>Service Unavailable</h1>', 502

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded = True)
    