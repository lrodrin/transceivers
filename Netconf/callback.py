import logging

from lxml import etree
from netconf import util

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"


def print_current_config(config):
    print("\n========== CURRENT RUNNING CONFIG: ==========\n")
    logging.debug(config)


def nse(xml):
    data = etree.fromstring(xml.replace(' ', '').replace('\n', ''))
    print(etree.tostring(data))
    result = util.xpath_filter_result(data, "node/*")
    # .//xmlns:node", namespaces={'xmlns': 'urn:node-topology'}
    print(etree.tounicode(result))


def call(config, fun):
    fun(config)


def get_changes(old_topology, new_topology):
    print("\n========== CONFIG HAS CHANGED ================\n")
    print_current_config(new_topology)
    print("\n========== CHANGES: ==========================================\n")
    logging.debug(old_topology)
    logging.debug(new_topology)
    print("\n========== END OF CHANGES ====================================\n")


def caller(old_topology, new_topology, funtion):
    funtion(old_topology, new_topology)
