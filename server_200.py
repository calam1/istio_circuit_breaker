from flask import Flask
import time

app = Flask(__name__)

@app.route('/index')
def get():
    return '<h1>Service Available</h1>', 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5005, threaded = True)
    