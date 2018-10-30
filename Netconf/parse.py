from __future__ import print_function

from pyangbind.lib.serialise import pybindIETFXMLEncoder
from binding import node_topology
from netconf import util
from xml.etree import ElementTree

from helpers import *

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

nt = node_topology()
nt.node.add("10.1.7.64")
nt.node.add("10.1.7.65")

for i, n in nt.node.iteritems():
    n.port.add("1")
    for j, p in n.port.iteritems():
        p.available_core.add("01")

data = pybindIETFXMLEncoder.serialise(nt)
# print(data)  # xml

write_file('test.xml', data)

xml_element_tree = ElementTree.parse('test.xml')

tree = ElementTree.parse('test.xml')
root = tree.getroot()
# print(ElementTree.tostring(root))
newroot = ElementTree.Element("nc:data")
# print(ElementTree.tostring(newroot))
# newroot.append(root)
newroot.insert(0, root)
print(ElementTree.tostring(newroot))

# with open('test.xml', 'rb') as f:
#     print('<data>{}</data>'.format(f.read()))

# with open('test.xml', 'rb') as f:
#     result = f.read()
#     # print('<data>{}</data>'.format(result))
#     t = '<data>{}</data>'.format(result)
#     print(t)

#print(ElementTree.tostring(newroot))

# print(ElementTree.tostring(data2, encoding='utf8', method='xml'))
# data.append(util.leaf_elm("node-topology:node", b))
# print(ElementTree.fromstring(data))


# merge XML
# xml_element_tree = data2
# xml_element_tree.extend(ElementTree.tostring(data))
# print(ElementTree.tostring(xml_element_tree, encoding="utf-8", method="xml").decode('utf-8'))

print("-"*30)
tree = ElementTree.parse('test.xml')
root = tree.getroot()
print(ElementTree.tostring(root))
data = util.elm("nc:data")
data.append(util.subelm(data, "node-topology:node", ElementTree.tostring(root)))

print(ElementTree.tostring(data))
