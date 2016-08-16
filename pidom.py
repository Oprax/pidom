# coding: utf-8

"""
Pi-Dom is module to make domotic with RPi and.
With use emit from `http://www.noopy.fr/raspberry-pi/domotique/`
`emit` can communicate with Chacon 54795
"""

import time
import subprocess
import pickle

from pathlib import Path

__all__ = ['PiDom', 'event']
__version__ = "0.2.0"
__author__ = "Oprax"


def event(name):
    """
    Pattern Observer with decorator,
    can execute function when event fire

    :param name: name of event
    :type name: str
    :rtype: function
    """
    event.sub = getattr(event, 'sub', dict())

    event.trigger = lambda e, data: [f(e, data) for f in event.sub[e]]

    def decorator(func):
        event.sub.setdefault(name, []).append(func)
        return func

    return decorator


@event('pidom.update')
def update(*args, **kwargs):
    """
    This function register 'pidom.update' event.
    This event is send each time a switch is turn on/off.
    """
    pass


@event('pidom.delete')
def delete(*args, **kwargs):
    """
    This function register 'pidom.delete' event.
    This event is send each time a switch is unsynchronize.
    """
    pass


class PiDom(object):
    """This class is a wrapper around `emit`"""
    def __init__(self):
        """Create property and call `PiDom.restore`"""
        self._bak = Path('~/.pidom.bin').expanduser()
        self._register = dict()
        self._groups = dict()
        self._id_available = set(range(0x00A0A400, 0x00A0A400 + 10))
        self.restore()

    def _change_state_device(self, name, state=True):
        """
        Change the state of a switch by using the device name

        :param name: Name of device
        :param state: The state we want, True for On and False for Off
        :type name: str
        :type state: bool
        """
        device_id = self._register[name]['device_id']
        self._register[name]['state'] = state
        # http://stackoverflow.com/a/14678150
        args = ['sudo', 'emit', '-d', format(device_id, '02X'), '-b', 'A1']
        if not state:
            args.append('-x')
        try:
            subprocess.run(args, check=True, stdout=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            print("https://github.com/Oprax/pidom#install")
            raise e
        event.trigger('pidom.update', {'name': name, 'state': state})

    def _sanitize(self, names):
        """
        Parse argument to return a list,
        args could be a device name, a group or just a list of devices

        :param names: a device name, a group or list of devices
        :param type: str | iterable
        :return: return a list of device(s)
        :rtype: iterable
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
        """
        Turn on a device or a group of devices

        :param names: Name(s) of device(s)
        :type names: str | iterable
        """
        names = self._sanitize(names)
        for name in names:
            self._change_state_device(name, state=True)

    def switch_off(self, names):
        """
        Turn off a device or a group of devices

        :param names: Name(s) of device(s)
        :type names: str | iterable
        """
        names = self._sanitize(names)
        for name in names:
            self._change_state_device(name, state=False)

    def toggle(self, names):
        """
        Reverse state of a device

        :param names: Name(s) of device(s)
        :type names: str | iterable
        """
        names = self._sanitize(names)
        for name in names:
            new_state = not self._register[name]['state']
            self._change_state_device(name, state=new_state)

    def synchronize(self, name):
        """
        Synchronize a new device and add it to register.

        When a Chacon is plugged in,
        while 5 seconds he listen and wait his id.

        :param name: device name given by user, most easy than 0x00A0A408
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
        event.trigger('pidom.delete', {'name': name, 'state': False})

    def clear(self):
        """Unsynchronize all device in register"""
        for name in self._register.keys():
            self.unsynchronize(name)

    def reset(self):
        """Reset all device in register"""
        for name in self._register.keys():
            self.switch_off(name)

    def state(self, name):
        """
        Return the state of device by name

        :param name: device name
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
        """
        A group is a list of device

        :param group_name: group name given by user
        :param devices: list of device in a group
        :type group_name: str
        :type devices: iterable
        """
        self._groups[group_name] = set()
        for device in devices:
            if device in self._register.keys():
                self.switch_off(device)
                self._groups[group_name].add(device)

    def rm_group(self, group_name):
        """
        Remove the list

        :param group_name: group name given by user
        :type group_name: str
        """
        self.switch_off(group_name)
        del self._groups[group_name]
