#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import requests
# import json
import array
import time

from os import sys, path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from lib.laser.laser import Laser
from lib.amp.amp import Amplifier

AMPLIFIER_ADDR = '3'

IP_AMPLIFIER_2 = '10.1.1.16'

IP_AMPLIFIER_1 = '10.1.1.15'

IP_LASER = '10.1.1.7'

LASER_ADDR = '11'

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

# Laser configuration
yenista = Laser(IP_LASER, LASER_ADDR)
yenista.wavelength(3, 1550.12)
yenista.power(3, 14.5)
yenista.enable(3, True)
time.sleep(5)
print(yenista.status(3))
print(yenista.test())
yenista.close()

# Amplifiers configuration
manlight_1 = Amplifier(IP_AMPLIFIER_1, AMPLIFIER_ADDR)
manlight_2 = Amplifier(IP_AMPLIFIER_2, AMPLIFIER_ADDR)
manlight_1.mode("APC", 5)
manlight_2.mode("APC", 3)
manlight_1.enable(True)
manlight_2.enable(True)
time.sleep(5)
print(manlight_1.status())
print(manlight_2.status())
print(manlight_1.test())
print(manlight_2.test())
manlight_1.close()
manlight_2.close()

# Waveshaper configuration

# int and float arrays of 512 positions examples
# bps = array.array('i', [0] * 512)
# pps = array.array('f', [0] * 512)
# print(bps)
# print(pps)
#
# bps = [0] * 512
# pps = [0.0] * 512
# print(bps)
# print(pps)

# url = 'http://10.1.1.10:5000/'  # REAL
url = 'http://127.0.0.1:5000/'  # TEST
headers = {"Content-Type": "application/json"}

# DAC configuration
# params = {'tx_ID': 0, 'trx_mode': 0, 'FEC': 'SD-FEC', 'bps': bps, 'pps': pps}
# request = requests.post(url + 'blue/dac', headers=headers, data=json.dumps(params))
# print(request.content)

# OSC configuration
# params = {'rx_ID': 0, 'trx_mode': 0, 'FEC': 'SD-FEC', 'bps': bps, 'pps': pps}
# request = requests.post(url + 'blue/osc', headers=headers, data=json.dumps(params))
# print(request.content)
