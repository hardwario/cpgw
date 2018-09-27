import zmq
import sys
import random

port = 5681
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect ("tcp://localhost:%s" % port)
socket.setsockopt(zmq.RCVTIMEO, 1000)

socket.send_string(sys.argv[1])
response = socket.recv_json()
if isinstance(response, list):
    for line in response:
        print(line)
else:
    print(response)
