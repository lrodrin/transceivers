import json

import numpy as np
import requests

from os import sys, path

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from lib.dac.dac import DAC

if __name__ == '__main__':
    headers = {"Content-Type": "application/json"}
    bn1 = np.array(np.ones(DAC.Ncarriers) * DAC.bps).tolist()
    bn2 = np.array(np.ones(DAC.Ncarriers)).tolist()
    En1 = np.array(np.ones(DAC.Ncarriers)).tolist()
    En2 = np.round(np.array(np.ones(DAC.Ncarriers) / np.sqrt(2)), 3).tolist()

    # print(bn1)
    # print(bn2)
    # print(En1)
    # print(En2)

    eq1 = eq2 = "MMSE"
    params = [{'id': 1, 'dac_out': 1, 'osc_in': 2, 'bn': bn1, 'En': En1, 'eq': eq1},
              {'id': 2, 'dac_out': 2, 'osc_in': 1, 'bn': bn2, 'En': En2, 'eq': eq2}]

    # configure
    request = requests.post('http://10.1.1.10:5000/api/dac_osc', headers=headers, data=json.dumps(params))
    print(request.json())

    # get
    request = requests.get('http://10.1.1.10:5000/api/dac_osc', headers=headers)
    print(request.json())
    request = requests.get('http://10.1.1.10:5000/api/dac_osc/1', headers=headers)
    print(request.json())
    request = requests.get('http://10.1.1.10:5000:5000/api/dac_osc/2', headers=headers)
    print(request.json())

    # delete
    request = requests.delete('hhttp://10.1.1.10:5000:5000/api/dac_osc/1', headers=headers)
    print(request.json())
    request = requests.get('http://10.1.1.10:5000:5000/api/dac_osc', headers=headers)
    print(request.json())
