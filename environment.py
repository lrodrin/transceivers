import collections
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

operations = collections.OrderedDict()  # operations configured on the WaveShaper
operations['1'] = [{'port_in': 1, 'port_out': 1, 'lambda0': 1550.99, 'att': 0.0, 'phase': 0.0, 'bw': 25}]
id = str(1)
if id not in operations.keys():
    operations[id] = [{'port_in': 1, 'port_out': 1, 'lambda0': 1550.99, 'att': 0.0, 'phase': 0.0, 'bw': 25}]
else:
    operations[id] += [{'port_in': 1, 'port_out': 1, 'lambda0': 1550.99, 'att': 0.0, 'phase': 0.0, 'bw': 25}]

print(operations)
