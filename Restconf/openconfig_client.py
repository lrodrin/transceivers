import json
import logging

import requests

logging.basicConfig(level=logging.DEBUG)

ip_server = '10.1.7.64'
url = 'http://%s:5001/api/vi/openconfig/' % ip_server
headers = {"Content-Type": "application/json"}

# test server
request = requests.get(url + 'hello', headers=headers)

# test local_assignment method from server
params_local_assignment = {'client': 1, 'och': 1}
request_local_assignment = requests.post(url + 'local_assignment', headers=headers,
                                         data=json.dumps(params_local_assignment))
if request_local_assignment:
    data = request_local_assignment.json()
    logging.debug(data)

# test optical_channel_configuration method from server
# params_optical_channel_configuration = {'och': 1, 'freq': 193.3e6, 'power': -2.97, 'mode': 0}
# request_optical_channel_configuration = requests.post(url + 'optical_channel', headers=headers,
#                                                       data=json.dumps(params_optical_channel_configuration))
# if request_optical_channel_configuration:
#     data = request_optical_channel_configuration.json()
#     logging.debug(data)
