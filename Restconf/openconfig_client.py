import json
import logging

import requests

logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    ip = "10.1.7.64"
    headers = {"Content-Type": "application/json"}
    params_lca = {'client': 'c1', 'och': 'och1'}
    params_occ = {'och': 'och1', 'freq': 193.4e6, 'power': 0, 'mode': 'HD-FEC'}

    # local channel assignment
    request = requests.post('http://%s:5000/api/vi/openconfig/local_channel_assignment' % ip, headers=headers,
                            data=json.dumps(params_lca))
    print(request.json())

    # optical channel configuration
    # request = requests.post('http://%s:5000/api/vi/openconfig/optical_channel' % ip, headers=headers,
    #                         data=json.dumps(params_occ))
    # print(request.json())
