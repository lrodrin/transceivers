#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import requests
# import json
import time

from lib.laser.laser import Laser

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

IP_LASER = '10.1.1.7'

LASER_ADDR = '11'

# Laser configuration
yenista = Laser(IP_LASER, LASER_ADDR)
yenista.wavelength(3, 1550.11)
yenista.power(3, 13.5)
yenista.enable(3, True)
time.sleep(5)
print(yenista.status(3))
print(yenista.test())
yenista.close()

# Amplifiers configuration
# Waveshaper configuration

# url = 'http://10.1.1.10:5000/'  # REAL
url = 'http://127.0.0.1:5000/'  # TEST
headers = {"Content-Type": "application/json"}

# DAC metro configuration
# params = {'trx_mode': 'METRO_1', 'tx_ID': 0}
# request = requests.post(url + 'metro/dac', headers=headers, data=json.dumps(params))
# print(request.content)

# OSC metro configuration
# params = {'rx_ID': 0, 'trx_mode': 0}
# request = requests.post(url + 'metro/osc', headers=headers, data=json.dumps(params))
# print(request.content)
