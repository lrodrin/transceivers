import json

import requests

if __name__ == '__main__':
    ip_server = '127.0.0.1'
    headers = {"Content-Type": "application/json"}
    request = requests.get('http://%s:5000/api/' % ip_server + 'hello', headers=headers, data=json.dumps("LAURA"))
    print(request.json())
