#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

print(sys.executable)

import os

print(os.getcwd())

import sys

print(sys.path)

from os import sys, path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from lib.laser.laser import Laser

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

IP_LASER = '10.1.1.7'

LASER_ADDR = '11'

yenista = Laser(IP_LASER, LASER_ADDR)
