Pi-Dom
======

# 1. Purpose

The goal of the project is to create a library can easely communicate with Chacon 54795 using HomeEasy protocol. I test my library on a Rasp Pi 1 B+. 

# 2. Install

## Dependecies
First you need to install `emit` on you Raspberry Pi, `emit` use [`wiringPi`](https://projects.drogon.net/raspberry-pi/wiringpi/) library.

`wiringpi` library :

```shell
cd /tmp
git clone git://git.drogon.net/wiringPi
cd wiringPi
sudo ./build
```

`emit` command :

```shell
cd /tmp
git clone https://github.com/landru29/chacon-rpi.git
cd chacon-rpi
make
sudo make install
```

you can test install with `emit -h`

You need root user to use `emit` see more information [here - french](http://www.noopy.fr/raspberry-pi/domotique/)

`emit` use pin 11 (GPIO 0) to communicate with the transmitter

## Pi-Dom

Use `pip` is the easiest way : 

```shell
pip install pidom
```
