import json
import requests

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

url = 'http://10.1.16.53:5000/api/'
headers = {"Content-Type": "application/json"}
# headers = {"Content-Type": "application/xml"}

# create slice
request = requests.post(url + 'transceiver/slice', headers=headers, data=json.dumps(
    {"sliceid": 1, "opticalchannelid": "1", "coreid": "Core19", "modeid": "LP01", "ncf": 137, "slot_width": 2}))
print(request.content)
request = requests.post(url + 'transceiver/slice', headers=headers, data=json.dumps(
    {"sliceid": 2, "opticalchannelid": 1, "coreid": "Core19", "modeid": "LP01", "ncf": 129, "slot_width": 2}))
print(request.content)
request = requests.post(url + 'transceiver/slice', headers=headers, data=json.dumps(
    {"sliceid": 3, "opticalchannelid": 1, "coreid": "Core19", "modeid": "LP01", "ncf": 129, "slot_width": 2}))
print(request.content)

request = requests.get(url + 'transceiver', headers=headers)
print(request.content)

# delete slice
request = requests.delete(url + 'transceiver/slice', headers=headers, data=json.dumps({"sliceid": 2}))
print(request.content)

request = requests.get(url + 'transceiver', headers=headers)
print(request.content)

# call config script
# startup_config = "python C:/Users/Laura/Desktop/scripts/config.py"
# request = requests.post(url + 'config', headers=headers, params=startup_config)
# print(request.content)
#
# # call monitor script
# startup_config = "python C:/Users/Laura/Desktop/scripts/monitor.py"
# request = requests.post(url + 'monitor', headers=headers, params=startup_config)
# print(request.content)
#
# # call matlab script
# startup_config = "python C:/Users/Laura/Desktop/scripts/matlab.py"
# request = requests.post(url + 'matlab', headers=headers, params=startup_config)
# print(request.content)