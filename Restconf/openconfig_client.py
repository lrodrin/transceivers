import logging

import requests

logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    ip_server = '10.1.7.64'
    params_xc = {'client': 0, 'och': 1}
    params_f = {'och': 0, 'freq': 1, 'power': 0, 'mode': 0}

    # test servers
    request = requests.get('http://%s:5001/api/vi/openconfig/' % ip_server + 'hello',    # TODO delete
                           headers={"Content-Type": "application/json"})

    # test local assignment from servers
    # request = requests.post('http://%s:5001/api/vi/openconfig/' % ip_server + 'local_assignment',
    #                         HEADERS={"Content-Type": "application/json"}, data=json.dumps(params_xc))
    if request:
        data = request.json()
        logging.debug(data)
    else:
        logging.error("Client not assigned to the optical channel")

    # test optical channel configuration from servers
    # request = requests.post('http://%s:5001/api/vi/openconfig/' % ip_server + 'optical_channel',
    #                         HEADERS={"Content-Type": "application/json"}, data=json.dumps(params_f))
    if request:
        data = request.json()
        logging.debug(data)
    else:
        logging.error("Optical Channel was not successfully configured")
