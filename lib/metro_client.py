import requests
import json
import time
# import array

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

url = 'http://10.1.1.10:5000/api/'  # REAL
# url = 'http://10.1.16.53:5000/api/' # TEST
headers = {"Content-Type": "application/json"}

# Laser configuration
params = {'channel': 3, 'wavelength': 1550.12, 'power': 13.5, 'status': True}
request = requests.post(url + 'laser', headers=headers, data=json.dumps(params))
print(request.content)

# Amplifier 10.1.1.15 configuration
params = {'ip': '10.1.1.15', 'mode': 'APC', 'power': 4, 'status': True}
request = requests.post(url + 'amp', headers=headers, data=json.dumps(params))
print(request.content)

time.sleep(5)

# Amplifier 10.1.1.16 configuration
params = {'ip': '10.1.1.16', 'mode': 'APC', 'power': 2, 'status': True}
request = requests.post(url + 'amp', headers=headers, data=json.dumps(params))
print(request.content)

# DAC metro configuration
# params = {'trx_mode': 'METRO_1', 'tx_ID': 0}
# request = requests.post(url + 'metro/dac', headers=headers, data=json.dumps(params))
# print(request.content)

# OSC metro configuration
# params = {'rx_ID': 0, 'trx_mode': 0}
# request = requests.post(url + 'metro/osc', headers=headers, data=json.dumps(params))
# print(request.content)


