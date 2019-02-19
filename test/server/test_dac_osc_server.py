import json
import requests

from os import sys, path

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from lib.dac.dac import DAC

if __name__ == '__main__':
    ip_server = '10.1.1.10'
    headers = {"Content-Type": "application/json"}
    bn = [float(DAC.bps)] * DAC.Ncarriers
    En = [float(1)] * DAC.Ncarriers
    params = {'conf_mode': 0, 'trx_mode': 0, 'tx_ID': 0, 'rx_ID': 0, 'bn': bn, 'En': En, 'eq': 0}

    request = requests.post('http://%s:5000/api/' % ip_server + 'dac_osc_configuration', headers=headers,
                            data=json.dumps(params))
    print(request.content)
