import requests, json
import pyangbind.lib.pybindJSON as pybindJSON

from binding import sliceable_transceiver_sdm

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"


url = 'http://10.1.16.53:5000/api/'
headers = {"Content-Type": "application/json"}

request = requests.post(url + 'transceiver/slice', headers=headers, data=json.dumps({"sliceid": "1"}))
print(request.content)

request = requests.post(url + 'transceiver/slice', headers=headers, data=json.dumps({"sliceid": "2"}))
print(request.content)

request = requests.get(url + 'transceiver', headers=headers)
print(request.content)

# request = requests.post(url + 'transceiver/slice/1', headers=headers, data=json.dumps({"opticalchannelid": "1"}))
# print(request.content)

request = requests.delete(url + 'transceiver/slice', headers=headers, data=json.dumps({"sliceid": "2"}))
print(request.content)

request = requests.get(url + 'transceiver', headers=headers)
print(request.content)

# call script
# request = requests.post(url + 'config', headers=headers, params="python test.py")
request = requests.post(url + 'config', headers=headers, params="python C:/Users/Laura/Desktop/test.py")
print(request.content)