#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import os
import sys
import time
import click
import click_log
import logging
import paho.mqtt.client
import simplejson as json
from cpgw.gateway import Gateway

logger = logging.getLogger()
handler = click_log.ClickHandler()
handler.setFormatter(click_log.ColorFormatter('%(asctime)s %(message)s'))
logger.addHandler(handler)


@click.command()
@click.option('--device', '-d', type=str, help='Device path.', required=True)
@click.option('--mqtt-host', help='MQTT host to connect to (default is localhost)', default="localhost", type=str)
@click.option('--mqtt-port', help='MQTT port to connect to (default is 1883)', default=1883, type=int)
@click_log.simple_verbosity_option(logger, default='INFO')
def run(device, mqtt_host, mqtt_port):
    mqttc = paho.mqtt.client.Client()
    mqttc.connect_async(mqtt_host, mqtt_port, keepalive=10)
    mqttc.loop_start()

    def on_recv(payload):
        logger.info(payload)
        topic = "node/%s/recv" % payload['id']
        del payload['id']
        mqttc.publish(topic, json.dumps(payload, use_decimal=True), qos=1)

    gw = Gateway(device)
    gw.on_recv = on_recv
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
