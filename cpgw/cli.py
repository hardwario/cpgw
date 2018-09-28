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
from cpgw.config import load_config

logging.basicConfig(format='%(asctime)s %(message)s')


@click.command()
@click.option('--config', '-c', 'config_file', type=click.File('r'), required=True, help='Configuration file.')
@click.option('--test', is_flag=True, help='Configuration file.')
@click_log.simple_verbosity_option(default='INFO')
def run(config_file, test):

    config = load_config(config_file)
    config_file.close()
    if test:
        click.echo("The configuration file seems ok")
        return

    logging.info("Process started")

    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://%s:%d" % (config['zmq']['publisher']['host'], config['zmq']['publisher']['port']))

    gw = Gateway(config['device'])
    gateway_id = gw.command("+CGSN")[0].split(':')[1].strip()

    if 'dispatcher' in config['zmq']:
        rw = RequestWorker(config['zmq']['dispatcher']['host'], config['zmq']['dispatcher']['port'], gw)

    def on_recv(payload):
        logging.info('Message from %s', payload['id'])
        logging.debug("payload %s", payload)
        payload['gw'] = gateway_id
        socket.send_json(payload)

    gw.on_recv = on_recv

    if 'dispatcher' in config['zmq']:
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
