import json
import logging
from os import sys, path

import requests

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    ip_server = '10.1.1.8'
    params = {'name': "wss_tx", 'configfile': "SN042561.wsconfig", 'lambda0': 1550.12, 'att': 0.0, 'phase': 0.0,
              'bandwidth': 25}
    # test server
    # request = requests.get('http://%s:5000/api/' % ip_server + 'hello',  # TODO delete
    #                        headers={"Content-Type": "application/json"}, data=json.dumps(params))

    # test wss server
    request = requests.post('http://%s:5000/api/' % ip_server + 'wss_configuration',
                            headers={"Content-Type": "application/json"}, data=json.dumps(params))
    if request:
        data = request.json()
        logging.debug(data)
    else:
        logging.error("The request could not be performed")