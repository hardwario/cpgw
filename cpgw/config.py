#!/usr/bin/env python3

import yaml
from schema import And, Optional, Schema, SchemaError


def port_range(port):
    return 0 <= port <= 65535


schema = Schema({
    'device': And(str, len),
    Optional('separator'): And(str, len),
    'zmq': {
        'publisher': {
            'host': And(str, len),
            'port': And(int, port_range)
        },
        Optional('dispatcher'): {
            'host': And(str, len),
            'port': And(int, port_range)
        }
    }
})


def load_config(config_file):
    config = yaml.safe_load(config_file)
    try:
        return schema.validate(config)
    except SchemaError as e:
        # Better error format
        error = str(e).splitlines()
        del error[1]
        raise Exception(' '.join(error))
