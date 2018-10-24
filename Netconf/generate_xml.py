from __future__ import print_function

from pyangbind.lib.serialise import pybindIETFXMLEncoder
from netconf import util
import pyangbind.lib.pybindJSON as pybindJSON

from binding import node_topology

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

nt = node_topology()
nt.node.add("10.1.7.64")
nt.node.add("10.1.7.65")

for i, n in nt.node.iteritems():
    n.port.add("1")
    for j, p in n.port.iteritems():
        p.available_core.add("01")

# print(pybindIETFXMLEncoder.serialise(nt))

print(nt.node.get())
