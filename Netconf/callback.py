import logging
from io import StringIO

from lxml import etree


__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"


def print_current_config(config):
    print("\n========== CURRENT RUNNING CONFIG: ==========\n")
    logging.debug(config)


def get_changes(config, old_topology, new_topology):
    print("\n========== CONFIG HAS CHANGED================\n")
    print_current_config(config)
    print("\n========== CHANGES: ==========================================\n")
    logging.debug(old_topology, new_topology)
    print("\n========== END OF CHANGES ====================================\n")


def caller(config, funtion):
    funtion(config)