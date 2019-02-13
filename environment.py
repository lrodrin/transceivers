import logging
import os
import sys

from os import sys, path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

print(sys.executable)
print(os.getcwd())
print(sys.path)

logger = logging.getLogger('logs/blue_agent.logs')
print(logger.name)
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%a, %d %b %Y '
#                                                                                                    '%H:%M:%S',
#                     filename='logs/blue_agent.logs', filemode='w')


logger.debug("HEHE")

if "up" in "Leia_DAC_up.m":
    print("YES")



import requests

url = 'http://10.1.7.64:5000/api/'
headers = {"Content-Type": "application/json"}

request = requests.get(url + 'hello', headers=headers)
print(request.status_code, request.content)

