import json
import requests

from os import sys, path

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from lib.dac.dac import DAC

if __name__ == '__main__':
    headers = {"Content-Type": "application/json"}
    bn = [float(DAC.bps)] * DAC.Ncarriers
    En = [float(1)] * DAC.Ncarriers
    params = [{'id': 1, 'dac_out': 1, 'osc_in': 1, 'bn': bn, 'En': En, 'eq': 0}]

    # configure
    request = requests.post('http://10.1.1.10:5000/api/dac_osc', headers=headers, data=json.dumps(params))
    print(request.content)

    # get
    #request = requests.get('http://10.1.1.10:5000/api/dac_osc', headers=headers)
    #print(request.content)
    #request = requests.get('http://10.1.1.10:5000/api/dac_osc/1', headers=headers)
    #print(request.content)
    #request = requests.get('http://10.1.1.10:5000:5000/api/dac_osc/2', headers=headers)
    #print(request.content)

    # delete
    #request = requests.delete('hhttp://10.1.1.10:5000:5000/api/dac_osc/1', headers=headers)
    #print(request.content)

    #request = requests.get('http://10.1.1.10:5000:5000/api/dac_osc', headers=headers)
    #print(request.content)
