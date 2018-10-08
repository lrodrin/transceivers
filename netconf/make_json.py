#!/usr/bin/env python

import pyangbind.lib.pybindJSON as pybindJSON
from netconf.binding import node_topology
from netconf.defaults import *
from  netconf.helpers import *
import argparse
import yaml
import sys


def make_json(yml):
    model = node_topology()
    for intf, conf in yml['interface'].iteritems():
        print("Instantiating model for {}".format(intf))
        intf_model = model.interfaces.interface.add(intf)
        intf_model.description = conf['description']
        ip_model = intf_model.ipv4.address.add(conf['address']['prefix'])
        ip_model.netmask = conf['address']['netmask']
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