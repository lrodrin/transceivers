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
def print_config_changes(config, old_node, new_node, op):
    print("\n ========== CONFIG HAS CHANGED, CURRENT RUNNING CONFIG: ==========\n")
    print_current_config(config)

    new_rows = new_node.xpath("xmlns:port", namespaces={'xmlns': 'urn:node-topology'})

    if old_node is not None:
        print("\n ========== CHANGES: =============================================\n")
        old_rows = old_node.xpath("xmlns:port", namespaces={'xmlns': 'urn:node-topology'})
        print("MODIFIED")
        print("OLD values")
        parse(old_rows, op)
        print("NEW values")
        parse(new_rows, op)
        # changes_list = new_change(old_list, new_list)
        # print("CHANGES", changes_list)

    elif old_node is None:
        print("\n ========== CHANGES: =============================================\n")
        parse(new_rows, op)

    print("\n\n ========== END OF CHANGES =======================================\n")
