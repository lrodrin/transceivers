import requests

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

url = 'http://10.1.1.10:5000/api/'
headers = {"Content-Type": "application/json"}
# headers = {"Content-Type": "application/xml"}

# call slice script
# startup_config = "python C:/Users/Laura/Desktop/scripts/matlab.py"
startup_config = "python C:/Users/cttc/Desktop/agent_bluespace/slice.py"
request = requests.post(url + 'slice', headers=headers, params=startup_config)
print(request.content)
