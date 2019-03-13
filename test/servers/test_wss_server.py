import json
import requests

if __name__ == '__main__':
    headers = {"Content-Type": "application/json"}
    params_wss1 = {'wss_id': 1, 'operation': [
        {'port_in': 1, 'port_out': 1, 'lambda0': 1550.52, 'att': 0.0, 'phase': 0.0, 'bw': 112.5}]}

    params_wss2 = {'wss_id': 2, 'operation': [
        {'port_in': 2, 'port_out': 1, 'lambda0': 1550.88, 'att': 0.0, 'phase': 0.0, 'bw': 50.0},
        {'port_in': 3, 'port_out': 1, 'lambda0': 1550.3, 'att': 0.0, 'phase': 0.0, 'bw': 50.0}]}

    # configure
    request = requests.post('http://10.1.1.10:5001/api/wss', headers=headers, data=json.dumps(params_wss1))
    print(request.json())
    request = requests.post('http://10.1.1.10:5001/api/wss', headers=headers, data=json.dumps(params_wss2))
    print(request.json())

    # get
    request = requests.get('http://10.1.1.10:5001/api/wss', headers=headers)
    print(request.json())
    request = requests.get('http://10.1.1.10:5001/api/wss/1', headers=headers)
    print(request.json())
    request = requests.get('http://10.1.1.10:5001/api/wss/2', headers=headers)
    print(request.json())

    # delete
    request = requests.delete('http://10.1.1.10:5001/api/wss/1', headers=headers)
    print(request.json())
    request = requests.get('http://10.1.1.10:5001/api/wss', headers=headers)
    print(request.json())
