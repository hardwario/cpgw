#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import os
import sys
import time
import re
import logging
import serial
import decimal
from threading import Condition, Lock, Thread, Event

context_prec1 = decimal.Context(prec=1)
context_prec2 = decimal.Context(prec=2)

items = (
    ("rssi", int),
    ("id", str),
    ("sequence", int),
    ("altitude", int),
    ("co2-conc", int),
    ("humidity", lambda x: decimal.Decimal(x, context_prec1)),
    ("illuminance", int),
    ("motion-count", int),
    ("orientation", int),
    ("press-count", int),
    ("pressure", int),
    ("sound-level", int),
    ("temperature", float),
    ("voc-conc", int),
    ("voltage", float)
)


class Gateway:

    def __init__(self, device):
        self._device = device
        self.on_line = None
        self.on_recv = None

        self._command = Lock()
        self._event = Event()
        self._response = None

    def run(self):
        self._ser = serial.Serial(self._device, baudrate=115200, timeout=3)
        time.sleep(0.5)
        self._ser.flush()
        self._ser.reset_input_buffer()
        self._ser.reset_output_buffer()

        while True:
            try:
                line = self._ser.readline()
            except serial.SerialException:
                self._ser.close()
                raise

            if line:
                logging.debug("read %s", line)

                line = line.decode().strip()

                if line[0] == '{':
                    continue

                if line[0] == '#':
                    continue

                if self.on_line:
                    self.on_line(line)

                if self.on_recv and line.startswith("$RECV:"):
                    payload = {}
                    values = line[7:].split(',')

                    for i, item in enumerate(items):
                        value = values[i]
                        payload[item[0]] = None if value == '' else item[1](value)

                    self.on_recv(payload)

                elif self._response != None:
                    if line == 'OK':
                        self._event.set()
                    elif line == 'ERROR':
                        self._response = None
                        self._event.set()
                    else:
                        self._response.append(line)

    def command(self, command):
        print("commad", command)
        with self._command:
            self._event.clear()
            command = 'AT' + command + '\r\n'
            self._response = []
            self._ser.write(command.encode('ascii'))
            self._event.wait()
            response = self._response
            self._response = None
            return response

    def start(self):
        """Run in thread"""
        Thread(target=self.run, args=[]).start()
