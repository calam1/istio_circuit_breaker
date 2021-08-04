import requests
import time
import sys
from datetime import datetime
import _thread

def timedisplay(t):
  return t.strftime("%H:%M:%S")

def get(url):
  try:
    stime = datetime.now()
    start = time.time()
    response = requests.get(url)
    etime = datetime.now()
    end = time.time()
    elapsed = end-start
    sys.stderr.write("STATUS: " + str(response.status_code) + ", START: " + timedisplay(stime) + ", END: " + timedisplay(etime) + ", TIME: " + str(elapsed)+"\n")
    sys.stdout.flush()
  except Exception as exc:
    sys.stderr.write("EXCEPTION: " + str(exc)+"\n")
    sys.stdout.flush()

# Initial 30 second wait to make sure Istio sidecar proxy is ready before we start sending requests
time.sleep(30)

while True:
  sc = int(datetime.now().strftime('%S'))
  time_range = [0, 20, 40]

  if sc not in time_range:
    time.sleep(1)
    continue

  sys.stderr.write("\n----------START BATCH----------\n")
  sys.stdout.flush()

  # Send 10 requests in parallel
  for i in range(10):
    _thread.start_new_thread(get, ("http://pyserver/index", ))

  time.sleep(2)

  