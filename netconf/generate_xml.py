import pyangbind.lib.serialise as pybindIETFXMLEncoder
from binding import node_topology

model = node_topology()
model.node.node_id = "10.1.7.64"
print(pybindIETFXMLEncoder.encode(model.node, filter=True))