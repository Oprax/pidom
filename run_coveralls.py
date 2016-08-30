#!/bin/env/python

import os

from subprocess import call


if __name__ == '__main__':
    print(os.environ)
    if 'TRAVIS' in os.environ:
        rc = call('coveralls')
        print('coveralls')
        raise SystemExit(rc)
