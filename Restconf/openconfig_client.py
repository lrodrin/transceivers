import json

import requests

url = 'http://10.1.1.10:5001/api/'
headers = {"Content-Type": "application/json"}

request = requests.get(url + 'hello', headers=headers)
print(request.status_code, request.content) 

# python_xc local_assignment
params = {'client': 1, 'och': 1}
request = requests.post(url + 'vi/openconfig/local_assignment', headers=headers, data=json.dumps(params))
print(request.content)

# python_f optical_channel_configuration
params = {'och': 1, 'freq': 193.3e6, 'power': -2.97, 'mode': 0}
# freq 193.3e6 = 1550.918
# freq = 193.4e6 = 1550.119
request = requests.post(url + 'vi/openconfig/optical_channel', headers=headers, data=json.dumps(params))
print(request.content)
