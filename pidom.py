# coding: utf-8

"""pi-dom is module to make domotic whith RPi.
With use emit from http://www.noopy.fr/raspberry-pi/domotique/"""

import time
import subprocess
import pickle

from pathlib import Path

__all__ = ['PiDom']
__version__ = "0.1.0"
__author__ = "Oprax"


class PiDom(object):
    """This class is a facility to communicate with
    Chacon 54795 using HomeEasy protocol.
    """
    def __init__(self, verbose=False):
        """Init list of available deivce id and a dict use as a register.
        Can define the verbosity

        :param verbose: Define the verbosity, default value is False
        :type verbose: bool

        :Example:
        >>> apidom = PiDom()
        >>> apidom = PiDom(verbose=False) # same than first example
        >>> apidom = PiDom(verbose=True)
        """
        self._verbose = verbose
        self._bak = Path('~/.pidom.bin').expanduser()
        self._register = dict()
        self._groups = dict()
        self._id_available = set(range(0x00A0A400, 0x00A0A400 + 10))
        self.restore()

    def _change_state_device(self, name, state=True):
        """
        Change the state of a switch by ``device_id``

        :param name: Name of device which change state
        :param state: The we want, True for On and False for Off
        :type name: str
        :type state: bool
        """
        device_id = self._register[name]['device_id']
        self._register[name]['state'] = state
        # http://stackoverflow.com/a/14678150
        args = ['sudo', 'emit', '-d', format(device_id, '02X'), '-b', 'A1']
        out = subprocess.PIPE
        if not state:
            args.append('-x')
        if self._verbose:
            out = None
        try:
            subprocess.run(args, check=True, stdout=out)
        except subprocess.CalledProcessError as e:
            raise e

    def _sanitize(self, names):
        """
        Can accept a device, a list of devices or a group
        So we parse args to return a list
        """
        if isinstance(names, str):
            if names in self._groups.keys():
                names = self._groups[names]
            else:
                names = [names]
        return names

    def backup(self):
        """
        Save register and groups in '~/.pidom.bin'
        Using ``pickle`` module to serialize data
        """
        if not self._bak.exists() and not self._bak.is_file():
            self._bak.touch()
        data = {
            'register': self._register,
            'groups': self._groups
        }
        pickle.dump(data, self._bak.open(mode='wb'))

    def restore(self):
        """
        Restore information (register and groups) from '~/.pidom.bin'
        Using ``pickle`` module to unserialize data
        Reconstruct id_available from register
        """
        if not self._bak.exists() and not self._bak.is_file():
            return
        data = pickle.load(self._bak.open(mode='rb'))
        self._groups = data['groups']
        self._register = data['register']
        for name in self._register.keys():
            self._id_available.remove(
                self._register[name]['device_id'])

    def switch_on(self, names):
        """Turn on a device or a group of devices

        :param names: Name(s) of device(s)
        :type names: str | iterable
        """
        names = self._sanitize(names)
        for name in names:
            self._change_state_device(name, state=True)

    def switch_off(self, names):
        """Turn off a device or a group of devices

        :param names: Name(s) of device(s)
        :type names: str | iterable"""
        names = self._sanitize(names)
        for name in names:
            self._change_state_device(name, state=False)

    def toggle(self, names):
        """Reverse state of a device"""
        names = self._sanitize(names)
        for name in names:
            new_state = not self._register[name]['state']
            self._change_state_device(name, state=new_state)

    def synchronize(self, name):
        """Synchronize a new switch and register him.

        When a switch is plugged in,
        while 5 seconds he listen and wait his id.

        :param name: Most easy than 0x00A0A408
        :type name: str
        :return: Id of the device
        :rtype: int
        """
        device_id = self._id_available.pop()
        self._register[name] = {
            'device_id': device_id,
            'state': False
        }
        t1 = time.time()
        t2 = time.time()
        while (t2 - t1) < 5:
            self.switch_on(name)
            t2 = time.time()
        self.switch_off(name)
        return device_id

    def unsynchronize(self, name):
        """Remove the device from register and place id on list of available"""
        self.switch_off(name)
        self._id_available.add(
            self._register[name]['device_id'])
        del self._register[name]

    def clear(self):
        """Unsynchronize all device in register"""
        for name in self._register.keys():
            self.unsynchronize(name)

    def reset(self):
        """Reset all switch in register"""
        for name in self._register.keys():
            self.switch_off(name)

    def state(self, name):
        """
        Return the state of device by name

        :param name: Device
        :type name: str
        :return: State of device
        :rtype: bool
        """
        return self._register[name]['state']

    @property
    def devices(self):
        """Return a list of device"""
        return list(self._register.keys())

    @property
    def groups(self):
        """Return a list of group"""
        return list(self._groups.keys())

    def new_group(self, group_name, devices):
        """A group is a list of device"""
        self._groups[group_name] = set()
        for device in devices:
            if device in self._register.keys():
                self.switch_off(device)
                self._groups[group_name].add(device)

    def rm_group(self, group_name):
        """Remove the list"""
        self.switch_off(group_name)
        del self._groups[group_name]
