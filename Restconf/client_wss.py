import json
import requests

if __name__ == '__main__':
    ip_server = '10.1.1.10'
    headers = {"Content-Type": "application/json"}
    configfile = "SN042561.wsconfig"
    params = {'name': "wss_tx", 'configfile': configfile, 'lambda0': 1550.12, 'att': 0.0,
              'phase': 0.0, 'bw': 25}

    request = requests.post('http://%s:5001/api/' % ip_server + 'wss_configuration', headers=headers,
                            data=json.dumps(params))
    print(request.content)
