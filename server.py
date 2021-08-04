from flask import Flask
import time

app = Flask(__name__)

@app.route('/index')
def get():
    time.sleep(5)
    return 'hello'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded = True)
    