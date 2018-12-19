import requests

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

url = 'http://10.1.1.10:5000/api/'
headers = {"Content-Type": "application/json"}

# DAC configuration
# params = "python C:/Users/Laura/Desktop/scripts/slice.py"
params = "python C:/Users/cttc/Desktop/agent_bluespace/slice.py"
request = requests.post(url + 'dac', headers=headers, params=params)
print(request.content)

# Laser configuration
params = {'channel': 3, 'wavelength': 1550.12, 'power': 14.5, 'status': True}
request = requests.post(url + 'laser', headers=headers, params=params)
print(request.content)

# Amplifier 10.1.1.15 configuration
params = {'ip': '10.1.1.15', 'mode': 'APC', 'power': 5, 'status': True}
request = requests.post(url + 'amp', headers=headers, params=params)
print(request.content)

# Amplifier 10.1.1.16 configuration
params = {'ip': '10.1.1.16', 'mode': 'APC', 'power': 3, 'status': True}
request = requests.post(url + 'amp', headers=headers, params=params)
print(request.content)
