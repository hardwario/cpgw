# COOPER Control Tool

[![Travis](https://img.shields.io/travis/hardwario/cpgw/master.svg)](https://travis-ci.org/hardwario/cpgw)
[![Release](https://img.shields.io/github/release/hardwario/cpgw.svg)](https://github.com/hardwario/cpgw/releases)
[![License](https://img.shields.io/github/license/hardwario/cpgw.svg)](https://github.com/hardwario/cpgw/blob/master/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/cpgw.svg)](https://pypi.org/project/cpgw/)


This is the Gateway tool for cooper dongle


## Installation

You can install **cpgw** directly from PyPI:


```sh
sudo pip3 install -U cpgw
```

> Note: You may need to use `sudo` before the command - it depends on the operating system used...


## Configuration

Insert this snippet to the file /etc/cooper/cpgw.yml:
```
device: /dev/ttyUSB0
zmq:
  publisher:
    host: 127.0.0.1
    port: 5680
  dispatcher:
    host: 127.0.0.1
    port: 5681
```


## Usage

```sh
cpgw -c /etc/cooper/cpgw.yml
```


### Start using systemd

Insert this snippet to the file `/etc/systemd/system/cpgw.service`:
```
[Unit]
Description=COOPER cpgw
After=network.target

[Service]
Type=simple
User=pi
ExecStart=/usr/local/bin/cpgw -c /etc/cooper/cpgw.yml
Restart=always
RestartSec=5
StartLimitIntervalSec=0

[Install]
WantedBy=multi-user.target
```

Start the service:

    systemctl start cpgw.service

Enable the service start on boot:

    systemctl enable cpgw.service

View the service log:

    journalctl -u cpgw.service -f


### Start using PM2

```sh
pm2 start `which python3` --name "cpgw" -- `which cpgw` -c /etc/cooper/cpgw.yml
```

### Usage as Python module

```python
from cpgw.gateway import Gateway

def on_recv(payload):
    print(payload)

gw = Gateway("/dev/ttyUSB0")
gw.on_recv = on_recv
gw.run()

```

## License

This project is licensed under the [**MIT License**](https://opensource.org/licenses/MIT/) - see the [**LICENSE**](LICENSE) file for details.
