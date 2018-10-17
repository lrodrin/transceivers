#!/usr/bin/env python

import argparse
import sys

import pyangbind.lib.pybindJSON as pybindJSON
import yaml

from netconf.binding import node_topology
from defaults import *
from helpers import *

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"


def make_json(yml):
    model = node_topology()
    model.node.node_id = yml['node']['node-id']
    new_port = model.node.port.add(yml['node']['port']['port-id'])
    new_port.available_core.add(yml['node']['port']['available-core']['core-id'])
    # for intf, conf in yml['interface'].iteritems():
    #     print("Instantiating model for {}".format(intf))
    #     intf_model = model.interfaces.interface.add(intf)
    #     intf_model.description = conf['description']
    #     ip_model = intf_model.ipv4.address.add(conf['address']['prefix'])
    #     ip_model.netmask = conf['address']['netmask']
    print("Done")
    return pybindJSON.dumps(model, mode='ietf')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--interface', '-i', default=YML, help="YAML Interface configuration file")
    args = parser.parse_args()

    yml = yaml.load(read_file(args.interface))

    result_json = make_json(yml)

    write_file('node_topology.json', result_json)


if __name__ == '__main__':
    sys.exit(main())
