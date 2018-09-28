# Cooper Control Tool

This is the Gateway tool for cooper dongle

## Installing

You can install **cpgw** directly from PyPI:


```sh
    sudo pip3 install -U cpgw
```

> Note: You may need to use `sudo` before the command - it depends on the operating system used...

## Usage

### As cli tool

```sh
cpgw -c config.yml
```

### As library

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
