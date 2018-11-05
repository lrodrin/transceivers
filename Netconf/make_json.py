import sys

from lxml import etree
from netconf import util
from pyangbind.lib.serialise import pybindIETFXMLEncoder, pybindIETFXMLDecoder

import binding
from helpers import *

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"


def make_json(filename, module_name):
    xml_root = open(filename, 'r').read()
    node_topo = pybindIETFXMLDecoder.decode(xml_root, binding, module_name)
    xml = pybindIETFXMLEncoder.serialise(node_topo)
    tree = etree.XML(xml)
    print(etree.tostring(tree, encoding='utf8', xml_declaration=True))

    data = util.elm("nc:data")
    data.append(tree)
    util.subelm(data, "node-topology:node", tree)
    return data


def main():
    xml = "test.xml"
    module_name = "node_topology"

    result = make_json(xml, module_name)
    write_file('node_topology.json', result)


if __name__ == '__main__':
    sys.exit(main())
