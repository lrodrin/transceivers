from __future__ import print_function

from pyangbind.lib.serialise import pybindIETFXMLEncoder

from binding import node_topology

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

nt = node_topology()
nt.node.add("127.0.0.1")
print(pybindIETFXMLEncoder.serialise(nt))
