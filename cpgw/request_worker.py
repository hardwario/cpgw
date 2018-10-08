import zmq
import logging
from threading import Thread


class RequestWorker(Thread):

    def __init__(self, host, port, gw):
        Thread.__init__(self)
        self.daemon = True
        addr = "tcp://%s:%s" % (host, port)
        logging.info("Publisher binding on %s", addr)
        context = zmq.Context()
        self._socket = context.socket(zmq.REP)
        self._socket.bind(addr)
        logging.info("Success bind on %s", addr)
        self._gw = gw
        self.__run = True

    def run(self):
        while self._socket:
            message = self._socket.recv_string()
            response = self._gw.command(message)
            self._socket.send_json(response)

    def kill(self):
        self._socket = None
