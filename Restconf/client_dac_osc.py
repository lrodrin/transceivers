import json
import logging

import requests

logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    ip_server = '10.1.1.10'
    params = {'conf_mode': 0, 'trx_mode': 0, 'tx_ID': 0, 'rx_ID': 0, 'bn': 2, 'En': 0, 'eq': 0}
    # test server
    # request = requests.get('http://%s:5000/api/' % ip_server + 'hello2',  # TODO delete
    #                        headers={"Content-Type": "application/json"}, data=json.dumps(params))
    # test dac and osc from server
    request = requests.post('http://%s:5000/api/' % ip_server + 'dac_osc_configuration',
                            headers={"Content-Type": "application/json"}, data=json.dumps(params))
    if request:
        data = request.json()
        logging.debug(data)
    else:
        logging.error("The request could not be performed")
