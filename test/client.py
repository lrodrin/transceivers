import requests, json
import pyangbind.lib.pybindJSON as pybindJSON

from binding import sliceable_transceiver_sdm

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"

modes = ["LP01", "LP11a", "LP11b", "LP21a", "LP21b", "LP02"]
model = sliceable_transceiver_sdm()
new_slice = model.transceiver.slice.add("1")

# for oc in new_slice.optical_channel.iteritems():
# 	print(oc)

def make_jason():
	pass

url = 'http://10.1.7.64:5000/api/'
headers = {"Content-Type": "application/json"}
request = requests.get(url + 'transceiver', headers=headers)
print(request.content)

request = requests.post(url + 'slice/1', headers=headers, data=json.dumps({"id": "1"}))
print(request.content)

request = requests.get(url + 'transceiver', headers=headers)
print(request.content)

request = requests.post(url + 'slice/1', headers=headers, data=json.dumps({"id": "2"}))
print(request.content)

request = requests.get(url + 'transceiver', headers=headers)
print(request.content)
