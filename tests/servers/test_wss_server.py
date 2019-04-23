import json
import requests

if __name__ == '__main__':
    headers = {"Content-Type": "application/json"}
    wss1 = {'wss_id': 1,
            'operations': [{'port_in': 1, 'port_out': 1, 'lambda0': 1550.12, 'att': 0.0, 'phase': 0.0, 'bw': 50.0}]}

    wss2 = {'wss_id': 2,
            'operations': [{'port_in': 2, 'port_out': 1, 'lambda0': 1550.12, 'att': 0.0, 'phase': 0.0, 'bw': 100.0},
                           {'port_in': 3, 'port_out': 1, 'lambda0': 1552.0, 'att': 0.0, 'phase': 0.0, 'bw': 100.0}]}

    # configure
    # request = requests.post('http://10.1.1.10:5001/api/wss', headers=headers, data=json.dumps(wss1))
    # print(request.json())
    request = requests.post('http://10.1.1.10:5001/api/wss', json=wss2)
    print(request)

    # get
    # request = requests.get('http://10.1.1.10:5001/api/wss', headers=headers)
    # print(request.json())
    # request = requests.get('http://10.1.1.10:5001/api/wss/1', headers=headers)
    # print(request.json())
    # request = requests.get('http://10.1.1.10:5001/api/wss/2', headers=headers)
    # print(request.json())

    # delete
    # request = requests.delete('http://10.1.1.10:5001/api/wss/1', headers=headers)
    # print(request.json())
    # request = requests.get('http://10.1.1.10:5001/api/wss', headers=headers)
    # print(request.json())
