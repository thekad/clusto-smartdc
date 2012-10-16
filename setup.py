#!/usr/bin/env python
#
# -*- mode:python; sh-basic-offset:4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim:set tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8:
#

import os
import setuptools
import sys


setuptools.setup(
    name = "clusto-smartdc",
    version = "0.1",
    packages = setuptools.find_packages('src'),
    author = 'Jorge Gallegos',
    author_email = "kad@blegh.net",
    description = "SmartDC (Joyent) extension for clusto",
    install_requires = [
        'smartdc',
        'ssh',
    ],
    entry_points = {
        'console_scripts': [
        ],
    },
    zip_safe = False,
    package_dir = { '': 'src' },
)

