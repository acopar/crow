#!/usr/bin/env python

from setuptools import setup, find_packages
import os

MAJOR               = 0
MINOR               = 2
MICRO               = 0
ISRELEASED          = False
VERSION             = '%d.%d.%d' % (MAJOR, MINOR, MICRO)

MODULE_PATH = os.path.dirname(os.path.abspath(__file__))

reqs = []
if os.path.isfile('requirements.txt'):
    with open('requirements.txt') as f:
        required = f.read().splitlines()
    reqs.extend(required)

params = {
    'data_files': [],
}

setup(name='crow',
    version='0.2',
    description='Parallel matrix factorization framework.',
    url='https://github.com/acopar/crow',
    author='Andrej Copar',
    license='LGPL',
    packages=find_packages(),
    entry_points = {
        "console_scripts": ['crow = crow.__main__:main',
                            'crow-runner = crow.__main__:run',
                            'crow-test = tests.__main__:main',
                            'crow-conv = crow.convert.__main__:main']
    },
    zip_safe=False,
    install_requires=reqs,
    **params
)

