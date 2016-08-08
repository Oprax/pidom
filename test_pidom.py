# coding: utf-8

from pathlib import Path

from pidom import PiDom

p = Path('~/.pidom.bin').expanduser()
if p.exists():
    p.unlink()


def test_init():
    pidom = PiDom()
    assert pidom._verbose is False
    assert pidom._register == dict()
    assert pidom._id_available == set(range(0x00A0A400, 0x00A0A400 + 10))

    pidom = PiDom(verbose=False)
    assert pidom._verbose is False
    assert pidom._register == dict()
    assert pidom._id_available == set(range(0x00A0A400, 0x00A0A400 + 10))

    pidom = PiDom(verbose=True)
    assert pidom._verbose is True
    assert pidom._register == dict()
    assert pidom._id_available == set(range(0x00A0A400, 0x00A0A400 + 10))


def test_synchronize():
    pidom = PiDom()
    assert len(pidom.devices) == 0
    pidom.synchronize('test')
    assert len(pidom.devices) == 1
    device_name = pidom.devices[0]
    assert device_name == 'test'
    device_id = pidom._register[device_name]['device_id']
    assert device_id not in pidom._id_available
    pidom.unsynchronize('test')
    assert len(pidom.devices) == 0
    assert device_id in pidom._id_available


def test_switch():
    pidom = PiDom()
    device_name = 'test'
    pidom.synchronize(device_name)
    assert pidom.state(device_name) is False
    pidom.switch_on(device_name)
    assert pidom.state(device_name) is True
    pidom.switch_off(device_name)
    assert pidom.state(device_name) is False


def test_toggle():
    pidom = PiDom()
    device_name = 'test'
    pidom.synchronize(device_name)
    assert pidom.state(device_name) is False
    pidom.toggle(device_name)
    assert pidom.state(device_name) is True
    pidom.toggle(device_name)
    assert pidom.state(device_name) is False


def test_reset():
    pidom = PiDom()
    device_name = 'test'
    pidom.synchronize(device_name)
    assert pidom.state(device_name) is False
    pidom.toggle(device_name)
    assert pidom.state(device_name) is True
    pidom.reset()
    assert pidom.state(device_name) is False


def test_group():
    pidom = PiDom()
    device_name1 = 'foo'
    device_name2 = 'bar'
    group_name = 'foobar'
    pidom.synchronize(device_name1)
    pidom.synchronize(device_name2)
    pidom.switch_on(device_name1)
    assert pidom.state(device_name1) is True
    pidom.new_group(group_name, [device_name1, device_name2])
    assert pidom.state(device_name1) is False
    assert pidom.state(device_name2) is False
    assert device_name1 in pidom._groups[group_name]
    assert device_name2 in pidom._groups[group_name]

    pidom.switch_on(group_name)
    assert pidom.state(device_name1) is True
    assert pidom.state(device_name2) is True

    pidom.switch_off(group_name)
    assert pidom.state(device_name1) is False
    assert pidom.state(device_name2) is False

    pidom.toggle(group_name)
    assert pidom.state(device_name1) is True
    assert pidom.state(device_name2) is True

    pidom.toggle(group_name)
    assert pidom.state(device_name1) is False
    assert pidom.state(device_name2) is False

    pidom.switch_on(group_name)

    pidom.rm_group(group_name)
    assert pidom.state(device_name1) is False
    assert pidom.state(device_name2) is False
    assert group_name not in pidom._groups.keys()
