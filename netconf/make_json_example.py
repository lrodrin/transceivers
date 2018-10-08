#!/usr/bin/env python

from __future__ import print_function, unicode_literals

import pyangbind.lib.pybindJSON as pybindJSON

from netconf.binding import node_topology

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

# Instantiate a copy of the pyangbind-kettle module
model = node_topology()

# Set a node-id for the node
model.node.node_id = "10.1.7.64"

# Add an entry to the port list
new_port = model.node.port.add("1")

# Use the get() method to see the content of the classes
# using the filter=True keyword to get only elements that
# are not empty or the default
print(model.node.get(filter=True))
# print(nt.node.port["01"].get(filter=True))

# Add a set of available-cores
for core in [("1", "Core1"), ("2", "Core2")]:
    ac = new_port.available_core.add(core[0])
    ac.core_id.available_core = core[1]

# Iterate through the available-cores added
for index, c in new_port.available_core.iteritems():
    print("%s: %s" % (index, c.core_id.available_core))

# Dump the entire instance as JSON in PyangBind format
print(pybindJSON.dumps(model))

# Dump the static routes instance as JSON in IETF format
print(pybindJSON.dumps(model.node, mode="ietf"))

# Load the "json/oc-lr.json" file into a new instance of
# "openconfig_local_routing". We import the module here, such that a new
# instance of the class can be created by the deserialisation code
# from netconf import binding

# new_nt = pybindJSON.load(os.path.join("json", "nt.json"), binding, "node_topology")

# Manipulate the data loaded
# print("Current port: %s" % new_nt.node.port["01"].port_id)
# new_nt.node.port["01"].port_id.set_port_id = "02"
# print("New port: %s" % new_nt.node.port["01"].port_id.set_port_id)
