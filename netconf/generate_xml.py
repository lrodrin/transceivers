import sys
print sys.path

from pyangbind.lib.serialise import pybindIETFXMLEncoder
from binding import node_topology

model = node_topology()
model.node.node_id = "10.1.7.64"
xmlEncoder=pybindIETFXMLEncoder()
print(pybindIETFXMLEncoder.serialise(model.node))
