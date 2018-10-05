#!/usr/bin/env python

import sys

import pyangbind.lib.pybindJSON as pybindJSON

from binding import node_topology

import binding
import os


def make_json():
    model = node_topology()
    model.node.node_id = '10.1.7.64'
    # print(pybindJSON.dumps(model))
    return pybindJSON.dumps(model, mode='ietf')


def main():
    import binding
    import os
    pybindJSON.load(os.path.join("json", "node_topology.json"), binding, "node_topology")


if __name__ == '__main__':
    sys.exit(main())
