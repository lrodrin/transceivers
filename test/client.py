import requests, json
import pyangbind.lib.pybindJSON as pybindJSON

from binding import sliceable_transceiver_sdm

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"


url = 'http://10.1.7.64:5000/api/'
headers = {"Content-Type": "application/json"}

request = requests.post(url + 'transceiver/slice', headers=headers, data=json.dumps({"sliceid": "1"}))
print(request.content)

request = requests.post(url + 'transceiver/slice/1', headers=headers, data=json.dumps({"opticalchannelid": "1"}))
print(request.content)

# request = requests.delete(url + 'transceiver/slice', headers=headers, data=json.dumps({"sliceid": "1"}))
# print(request.content)

request = requests.get(url + 'transceiver', headers=headers)
print(request.content)