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
try:
    import fcntl
except ImportError:
    fcntl = None


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

        logging.info("Connecting on device %s", self._device)
        self._ser = serial.Serial(self._device, baudrate=115200, timeout=3)

        if fcntl and self._ser:
            try:
                fcntl.flock(self._ser.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except Exception as e:
                raise Exception('Could not lock device %s' % self._device)

        logging.info("Success connect on device %s", self._device)

        self._ser.flush()
        self._ser.reset_input_buffer()
        self._ser.reset_output_buffer()
        time.sleep(0.5)

        self.is_run = False

    def run(self):
        self.is_run = True
        while self.is_run:
            self._loop()

    def _loop(self):
        try:
            line = self._ser.readline()
        except serial.SerialException as e:
            logging.error("SerialException %s", e)
            self._ser.close()
            raise

        if line:
            logging.debug("Read line %s", line)

            line = line.decode().strip()

            if line[0] == '{':
                return

            if line[0] == '#':
                return

            if self.on_line:
                self.on_line(line)

            if self.on_recv and line.startswith("$RECV:"):
                payload = {}
                values = line[7:].split(',')

                for i, item in enumerate(items):
                    value = values[i]
                    payload[item[0]] = None if value == '' else item[1](value)

                self.on_recv(payload)

            elif self._response is not None:
                if line == 'OK':
                    self._event.set()
                elif line == 'ERROR':
                    self._response = None
                    self._event.set()
                else:
                    self._response.append(line)

    def command(self, command):
        with self._command:
            logging.debug("Command %s", command)
            self._event.clear()
            command = 'AT' + command + '\r\n'
            self._response = []
            self._ser.write(command.encode('ascii'))
            if self.is_run:
                self._event.wait()
            else:
                while not self._event.is_set():
                    self._loop()
            response = self._response
            self._response = None
            return response

    def get_cgsn(self):
        response = self.command("+CGSN")
        if not response:
            raise Exception("Command AT+CGSN not work.")
        return response[0].split(':')[1].strip()

    def start(self):
        """Run in thread"""
        Thread(target=self.run, args=[]).start()
