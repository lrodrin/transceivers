import json
import logging
import requests

from os import sys, path

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from lib.dac.dac import DAC

logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    ip_server = '10.1.1.10'
    headers = {"Content-Type": "application/json"}

    En = [float(1)] * DAC.Ncarriers
    bn = [float(DAC.bps)] * DAC.Ncarriers
    params = {'conf_mode': 0, 'trx_mode': 1, 'tx_ID': 0, 'rx_ID': 0, 'bn': bn, 'En': En, 'eq': 0}
    # test server
    # request = requests.get('http://%s:5000/api/' % ip_server + 'hello2', headers=headers, data=json.dumps(params))

    # test dac and osc from server
    request = requests.post('http://%s:5000/api/' % ip_server + 'dac_osc_configuration', headers=headers, data=json.dumps(params))

    if request:
        data = request.json()
        logging.debug(data)
    else:
        logging.error("The request was wrongly formulated")
