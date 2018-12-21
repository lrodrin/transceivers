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
params = {'channel': 3, 'wavelength': 1550.12, 'power': 14.5, 'status': True}
request = requests.post(url + 'laser', headers=headers, data=json.dumps(params))
print(request.content)

# Amplifier 10.1.1.15 configuration
params = {'ip': '10.1.1.15', 'mode': 'APC', 'power': 5, 'status': True}
request = requests.post(url + 'amp', headers=headers, data=json.dumps(params))
print(request.content)

time.sleep(5)

# Amplifier 10.1.1.16 configuration
params = {'ip': '10.1.1.16', 'mode': 'APC', 'power': 3, 'status': True}
request = requests.post(url + 'amp', headers=headers, data=json.dumps(params))
print(request.content)

# bps = array.array('i', [0] * 512)
# pps = array.array('f', [0] * 512)
# print(bps)
# print(pps)

# bps = [0] * 512
# pps = [0.0] * 512
# print(bps)
# print(pps)

# DAC bluespace configuration
# params = {'tx_ID': 0, 'trx_mode': 0, 'FEC': 'SD-FEC', 'bps': bps, 'pps': pps}
# request = requests.post(url + 'blue/dac', headers=headers, data=json.dumps(params))
# print(request.content)

# OSC bluespace configuration
# params = {'rx_ID': 0, 'trx_mode': 0, 'FEC': 'SD-FEC', 'bps': bps, 'pps': pps}
# request = requests.post(url + 'blue/osc', headers=headers, data=json.dumps(params))
# print(request.content)
