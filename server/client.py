import requests

from binding import sliceable_transceiver_sdm

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"


url = 'http://10.1.7.64:5000/transceiver'
headers = {'Content-Type': 'application/json', 'Accept-Charset': 'UTF-8'}
request = requests.get(url, headers=headers)
print(request.json())


request = requests.po