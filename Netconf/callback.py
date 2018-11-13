import logging

from lxml import etree
from netconf import util

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"


# Function to print current configuration state
def print_current_config(config):
    print("\n========== CURRENT RUNNING CONFIG: ==========\n")
    logging.debug(etree.tostring(config))


def get_changes(config, old_value, new_value):
    print("\n========== CONFIG HAS CHANGED ================\n")
    print_current_config(config)
    
    if old_value is not None:
        print("\n========== CHANGES: ==========================================\n")
        logging.debug(etree.tostring(old_value))
        logging.debug(etree.tostring(new_value))
    elif old_value is None:
        print("\n========== CHANGES: ==========================================\n")
        logging.debug(etree.tostring(new_value))
    
    print("\n========== END OF CHANGES ====================================\n")

# CREATED:  /node-topology:node[node-id='10.1.7.65']/port[port-id='65792']/available-core[core-id='01']/occupied-frequency-slot[slot-id='604045311'] (list instance)
# CREATED:  /node-topology:node[node-id='10.1.7.65']/port[port-id='65792']/available-core[core-id='01']/occupied-frequency-slot[slot-id='604045311']/slot-id = 604045311

# def caller(old_topology, new_topology, funtion):
#     funtion(old_topology, new_topology)

# def nse(xml):
#     data = etree.fromstring(xml.replace(' ', '').replace('\n', ''))
#     print(etree.tostring(data))
#     result = util.xpath_filter_result(data, "node/*")
#     # .//xmlns:node", namespaces={'xmlns': 'urn:node-topology'}
#     print(etree.tounicode(result))
#
#
# def call(config, fun):
#     fun(config)
