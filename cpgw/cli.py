#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import os
import sys
import time
import click
import click_log
import logging
import simplejson as json
import zmq
from cpgw.gateway import Gateway
from cpgw.request_worker import RequestWorker


logger = logging.getLogger()
handler = click_log.ClickHandler()
handler.setFormatter(click_log.ColorFormatter('%(asctime)s %(message)s'))
logger.addHandler(handler)


@click.command()
@click.option('--device', '-d', type=str, help='Device path.', required=True)
@click.option('--port', '-p', type=int, help='Port', required=True)
@click_log.simple_verbosity_option(logger, default='INFO')
def run(device, port):

    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://*:%s" % port)

    gw = Gateway(device)
    gateway_id = gw.command("+CGSN")[0].split(':')[1].strip()

    rw = RequestWorker('0.0.0.0', port + 1, gw)

    def on_recv(payload):
        logger.debug("recv %s", payload)
        payload['gw'] = gateway_id
        socket.send_json(payload)

    gw.on_recv = on_recv

    rw.start()

    gw.run()


def main():
    try:
        run()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        click.echo(str(e), err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
