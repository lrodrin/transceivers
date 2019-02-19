import json
import requests

if __name__ == '__main__':
    wss_id = 1  # 1 or 2
    headers = {"Content-Type": "application/json"}
    params = [{'port_in': 1, 'port_out': 1, 'lambda0': 1550.12, 'att': 0.0, 'phase': 0.0, 'bw': 25},
              {'port_in': 2, 'port_out': 1, 'lambda0': 1550.12, 'att': 0.0, 'phase': 0.0, 'bw': 25},
              {'port_in': 3, 'port_out': 1, 'lambda0': 1550.12, 'att': 0.0, 'phase': 0.0, 'bw': 25},
              {'port_in': 4, 'port_out': 1, 'lambda0': 1550.12, 'att': 0.0, 'phase': 0.0, 'bw': 25}]

    request = requests.post('http://10.1.7.64:5001/api/wss', headers=headers, data=json.dumps(params))
    print(request.content)

    # request = requests.get('http://10.1.1.10:5001/api/wss/%s' % wss_id, headers=headers, data=json.dumps(params))
    # print(request.content)
