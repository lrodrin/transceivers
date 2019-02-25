import collections
import json
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

del operations[id]
print(operations)

params_wss_2 = {'wss_id': 2, 'operation': [{'port_in': 1, 'port_out': 1, 'lambda0': 1550.99, 'att': 0.0,
                                            'phase': 0.0, 'bw': 25},
                                           {'port_in': 2, 'port_out': 1, 'lambda0': 1550.12, 'att': 0.0, 'phase': 0.0,
                                            'bw': 25},
                                           {'port_in': 3, 'port_out': 1, 'lambda0': 1549.3, 'att': 0.0, 'phase': 0.0,
                                            'bw': 25}, {'port_in': 4,
                                                        'port_out': 1, 'lambda0': 1548.5, 'att': 0.0, 'phase': 0.0,
                                                        'bw': 25}]}

print(params_wss_2['operation'])

from collections import Counter

c = Counter()
for item in params_wss_2['operation']:
    c[item["port_in"]] += 1

print(len(c))

logical_associations = collections.OrderedDict()
wanted_keys = ('dac_out', 'osc_in', 'eq')
params_dac_osc = [{'id': 1, 'dac_out': 1, 'osc_in': 1, 'eq': 0}, {'id': 2, 'dac_out': 1, 'osc_in': 1, 'eq': 0}]

data = json.dumps(params_dac_osc)

for item in params_dac_osc:
    id = item['id']
    filtered_assoc = dict(zip(wanted_keys, [item[k] for k in wanted_keys]))  # assoc - ['id']
    print(filtered_assoc)
    logical_associations[id] = filtered_assoc

print(logical_associations)
