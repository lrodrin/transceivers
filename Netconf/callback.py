import logging

from lxml import etree
from compare import *
# TODO treure modularitat compare

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"


# function to print current configuration
def print_current_config(config):
    logging.debug(etree.tostring(config))


# function to print configuration changes
def print_config_changes(config, old_node, new_node, operation):
    print("\n ========== CONFIG HAS CHANGED, CURRENT RUNNING CONFIG: ==========\n")
    print_current_config(config)

    rows_2 = new_node.xpath("xmlns:port", namespaces={'xmlns': 'urn:node-topology'})

    if old_node is not None:
        print("\n ========== CHANGES: =============================================\n")
        rows_1 = old_node.xpath("xmlns:port", namespaces={'xmlns': 'urn:node-topology'})
        old_values = parse(rows_1, operation)
        new_values = parse(rows_2, operation)
        print("OLD values", old_values)
        print("NEW values", new_values)
        print("CHANGES", new_change(old_values, new_values))

    elif old_node is None:
        print("\n ========== CHANGES: =============================================\n")
        print("NEW_values", parse(rows_2, operation))

    print("\n\n ========== END OF CHANGES =======================================\n")

# CREATED:  /node-topology:node[node-id='10.1.7.65']/port[port-id='65792']/available-core[
# core-id='01']/occupied-frequency-slot[slot-id='604045311'] (list instance) CREATED:  /node-topology:node[
# node-id='10.1.7.65']/port[port-id='65792']/available-core[core-id='01']/occupied-frequency-slot[
# slot-id='604045311']/slot-id = 604045311
