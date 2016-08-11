Pi-Dom
======

# Purpose

The goal of the project is to create a library can easely communicate with Chacon 54795 using HomeEasy protocol. I test my library with a Raspberry Pi 1 model B+.

```python
from pidom import PiDom

pidom = PiDom()
pidom.synchronize('tv') # 'tv' is off
pidom.switch_on('tv') # 'tv' is on (obvious)
pidom.toggle('tv') # 'tv' is off
pidom.synchronize('light') # add new device
pidom.new_group('living-room', ['tv', 'light']) # switch off 'tv' & 'light'
pidom.toggle('living-room') # # switch on 'tv' & 'light'
pidom.backup() # save device and group with pickle in '~/.pidom.bin'
```

More example in `test_pidom.py`.

# Install

## Dependecies

First you need to install [`emit`](http://www.noopy.fr/raspberry-pi/domotique/) on you Raspberry Pi, `emit` use [`wiringPi`](https://projects.drogon.net/raspberry-pi/wiringpi/) library.

install `wiringpi` library :

```shell
cd /tmp
git clone git://git.drogon.net/wiringPi
cd wiringPi
sudo ./build
```

install `emit` command :

```shell
cd /tmp
git clone https://github.com/landru29/chacon-rpi.git
cd chacon-rpi
make
sudo make install
```

You can test install with `emit -h`

`emit` use pin 11 (GPIO 0) to communicate with the transmitter.

## Pi-Dom

Use `pip` is the easiest way : 

```shell
pip install pidom
```
