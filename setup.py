#!/usr/bin/env python3

import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand

import pidom


class Tox(TestCommand):
    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import tox
        import shlex
        args = self.tox_args
        if args:
            args = shlex.split(self.tox_args)
        errno = tox.cmdline(args=args)
        sys.exit(errno)


try:
    ldesc = open('README.md').read()
except:
    ldesc = ("The goal of the project is to create a library can "
             "easely communicate with Chacon 54795 using HomeEasy protocol."
             " I test my library on a Rasp Pi 1 B+.")

setup(
    name='pidom',
    version=pidom.__version__,
    author=pidom.__author__,
    author_email='oprax@me.com',
    description=pidom.__doc__,
    py_modules=['pidom'],
    long_description=ldesc,
    license='https://opensource.org/licenses/MIT',
    include_package_data=True,
    tests_require=['tox'],
    cmdclass={'test': Tox},
    url='https://github.com/Oprax/pidom',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Programming Language :: Python :: 3.5",
        "Topic :: Home Automation",
        "Operating System :: POSIX :: Linux",
        "License :: OSI Approved :: MIT License"
    ]
)
