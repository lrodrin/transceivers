import requests
import json
import time

from os import sys, path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from lib.laser.laser import Laser
from lib.amp.amp import Amplifier
# from lib.wss.wss import Wss

AMPLIFIER_ADDR = '3'
IP_AMPLIFIER_2 = '10.1.1.16'
IP_AMPLIFIER_1 = '10.1.1.15'
IP_LASER = '10.1.1.7'
LASER_ADDR = '11'

# Laser configuration
yenista = Laser(IP_LASER, LASER_ADDR)
yenista.wavelength(3, 1560.12)
yenista.power(3, 7.5)
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

# url = 'http://10.1.1.10:5000/api/'  # REAL
url = 'http://127.0.0.1:5000/api/'  # TEST
headers = {"Content-Type": "application/json"}

request = requests.get(url + 'hello', headers=headers)
print(request.content)

# DAC metro configuration
params = {'trx_mode': 0, 'tx_ID': 0}
request = requests.post(url + 'metro/dac', headers=headers, data=json.dumps(params))
print(request.content)

# OSC metro configuration
# params = {'rx_ID': 0, 'trx_mode': 0}
# request = requests.post(url + 'api/metro/osc', headers=headers, data=json.dumps(params))
# print(request.content)
