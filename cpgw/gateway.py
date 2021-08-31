#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import decimal
import logging
import platform
import time
from ctypes import *
from threading import Event, Lock, Thread

import serial

try:
    import fcntl
except ImportError:
    fcntl = None


context_prec1 = decimal.Context(prec=1)
context_prec2 = decimal.Context(prec=2)

recv_start = (
    ("rssi", int),
    ("id", str),
    ("header", int),
    ("sequence", int),
    ("uptime", int),
)

recv_type_lut = {
    1: {'type': 'beacon',
        'items': (
            ("altitude", int),
            ("co2_conc", int),
            ("humidity", lambda x: decimal.Decimal(x, context_prec1)),
            ("illuminance", int),
            ("motion_count", int),
            ("orientation", int),
            ("press_count", int),
            ("pressure", int),
            ("sound_level", int),
            ("temperature", lambda x: decimal.Decimal(x, context_prec2)),
            ("voc_conc", int),
            ("voltage", lambda x: decimal.Decimal(x, context_prec2))
        )},
    2: {'type': 'sound',
        'items': (
            ("min", int),
            ("max", int),
        )}
}

items_v1_0_x = (
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
    ("temperature", lambda x: decimal.Decimal(x, context_prec2)),
    ("voc-conc", int),
    ("voltage", lambda x: decimal.Decimal(x, context_prec2))
)


class Gateway:

    def __init__(self, device, separator):
        self._ser = None
        self._device = device
        self.on_line = None
        self.on_recv = None

        self._command_mutex = Lock()
        self._event = Event()
        self._response = None

        logging.info("Connecting on device %s", self._device)
        self._ser = serial.Serial(self._device, baudrate=115200, timeout=3)

        self._lock()
        self._speed_up()

        logging.info("Success connect on device %s", self._device)

        self._ser.flush()
        self._ser.reset_input_buffer()
        self._ser.reset_output_buffer()
        time.sleep(0.5)
        self._ser.write(b'\x1b')

        self.is_run = False

        self._command('')

        cgmr = self.get_cgmr()
        self._old_recv = cgmr.startswith("1.0.") or cgmr.startswith("v1.0.")

        logging.info("FW: %s", self.command('I')[0])

        self._recv_type_lut = {}
        for header in recv_type_lut:
            items = []
            for item in recv_type_lut[header]['items']:
                items.append((item[0].replace('_', separator), item[1]))
            self._recv_type_lut[header] = {
                'type': recv_type_lut[header]['type'],
                'items': tuple(items),
            }

    def __del__(self):
        self._unlock()
        try:
            self._ser.close()
        except Exception as e:
            pass
        self._ser = None

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

                if self._old_recv:
                    for i, item in enumerate(items_v1_0_x):
                        value = values[i]
                        payload[item[0]] = None if value == '' else item[1](value)
                else:
                    for i, item in enumerate(recv_start):
                        value = values[i]
                        payload[item[0]] = None if value == '' else item[1](value)

                    recv_type = self._recv_type_lut.get(payload['header'], None)

                    if recv_type:
                        del payload['header']
                        payload['type'] = recv_type['type']
                        for i, item in enumerate(recv_type['items']):
                            value = values[i + 5]
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

    def _command(self, command):
        with self._command_mutex:
            logging.debug("Command AT%s", command)
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

    def command(self, command, repeat=3):
        for i in range(repeat):
            response = self._command(command)
            if response is None:
                time.sleep(0.5)
                continue
            return response
        raise Exception("Command %s not work." % command)

    def get_cgsn(self):
        response = self.command("+CGSN")
        return response[0].split(':')[1].strip()

    def get_cgmr(self):
        response = self.command("+CGMR")
        return response[0].split(':')[1].strip()

    def start(self):
        """Run in thread"""
        Thread(target=self.run, args=[]).start()

    def _lock(self):
        if not fcntl or not self._ser:
            return
        try:
            fcntl.flock(self._ser.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except Exception as e:
            raise Exception('Could not lock device %s' % self._device)

    def _unlock(self):
        if not fcntl or not self._ser:
            return
        fcntl.flock(self._ser.fileno(), fcntl.LOCK_UN)

    def _speed_up(self):
        if not fcntl:
            return
        if platform.system() != 'Linux':
            return

        TIOCGSERIAL = 0x0000541E
        TIOCSSERIAL = 0x0000541F
        ASYNC_LOW_LATENCY = 0x2000

        class serial_struct(Structure):
            _fields_ = [("type", c_int),
                        ("line", c_int),
                        ("port", c_uint),
                        ("irq", c_int),
                        ("flags", c_int),
                        ("xmit_fifo_size", c_int),
                        ("custom_divisor", c_int),
                        ("baud_base", c_int),
                        ("close_delay", c_ushort),
                        ("io_type", c_byte),
                        ("reserved_char", c_byte * 1),
                        ("hub6", c_uint),
                        ("closing_wait", c_ushort),
                        ("closing_wait2", c_ushort),
                        ("iomem_base", POINTER(c_ubyte)),
                        ("iomem_reg_shift", c_ushort),
                        ("port_high", c_int),
                        ("iomap_base", c_ulong)]

        buf = serial_struct()

        try:
            fcntl.ioctl(self._ser.fileno(), TIOCGSERIAL, buf)
            buf.flags |= ASYNC_LOW_LATENCY
            fcntl.ioctl(self._ser.fileno(), TIOCSSERIAL, buf)
        except Exception as e:
            pass
