from types import MethodDescriptorType
from flask import Flask
import time

app = Flask(__name__)

failFlag = False

@app.route('/index')
def get():
    if not failFlag:
        return '<h1>Service Available</h1>', 200
    else:
        return '<h1>Service Unavailable</h1>', 502

@app.route('/fail', methods=['POST'])
def fail():
    global failFlag
    failFlag = True
    return '<h1>Flag is set to fail', 200
    
@app.route('/pass', methods=['POST'])
def unfail():
    global failFlag
    failFlag = False
    return '<h1>Flag is set to pass', 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded = True)
    