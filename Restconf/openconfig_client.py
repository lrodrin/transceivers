import json
import logging

import requests

logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    ip = "10.1.7.64"
    headers = {"Content-Type": "application/json"}
    params_lca = {'name': 'c1', 'och': 'channel-101', 'status': 'enabled', 'type': 'client'}
    params_occ = {'frequency': '192300000', 'mode': '111', 'name': 'channel-101', 'power': '10.0', 'status': 'enabled',
                  'type': 'optical_channel'}

    # local channel assignment
    request = requests.post('http://%s:5000/api/v1/openconfig/logical_channel_assignment' % ip, headers=headers,
                            data=json.dumps(params_lca))
    print(request.json())

    # optical channel configuration
    # request = requests.post('http://%s:5000/api/v1/openconfig/optical_channel' % ip, headers=headers,
    #                         data=json.dumps(params_occ))
    # print(request.json())

    # remove local channel assignment
    request = requests.delete('http://%s:5000/api/v1/openconfig/logical_channel_assignment/c1' % ip, headers=headers)
    print(request.json())

    # remove optical channel configuration
    # request = requests.delete('http://%s:5000/api/v1/openconfig/optical_channel/channel-101' % ip, headers=headers)
    # print(request.json())
