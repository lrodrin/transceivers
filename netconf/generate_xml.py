from __future__ import print_function

from pyangbind.lib.serialise import pybindIETFXMLEncoder

from binding import node_topology

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

model = node_topology()
model.node.node_id = "10.1.7.64"
print(pybindIETFXMLEncoder.serialise(model))
