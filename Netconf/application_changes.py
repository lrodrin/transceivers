import logging

from compare import *

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
        rows_1 = old_value.xpath("xmlns:port", namespaces={'xmlns': 'urn:node-topology'})
        rows_2 = new_value.xpath("xmlns:port", namespaces={'xmlns': 'urn:node-topology'})
        print("OLD_values", parse(rows_1))
        print("NEW_values", parse(rows_2))
        old_list = parse(rows_1)
        new_list = parse(rows_2)
        print("CHANGES", new_change(old_list, new_list))
    elif old_value is None:
        print("\n========== CHANGES: ==========================================\n")
        rows_2 = new_value.xpath("xmlns:port", namespaces={'xmlns': 'urn:node-topology'})
        print("NEW_values", parse(rows_2))

    print("\n========== END OF CHANGES ====================================\n")
