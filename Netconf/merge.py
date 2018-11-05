from __future__ import print_function
from lxml import etree

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

tree = etree.parse("test.xml")
print(tree.xpath(".//xmlns:node-id", namespaces={'xmlns': 'urn:node-topology'}))

topo = tree.xpath(".//xmlns:node-id", namespaces={'xmlns': 'urn:node-topology'})

for elem in topo:
    print(elem.text)

print("-"*10)

# for elem in topo:
#     for element in tree.iter('{urn:node-topology}node-id'):
#         # print("%s - %s" % (element.tag, element.text))
#         # print(elem.text, element.text)
#         if elem.text == element.text:
#             print("YES")
#         else:
#             print("NO")

# for element in tree.iter('{urn:node-topology}node-id'):
#     print(element.text)
#     if element in topo:
#         print("YES")
#     else:
#         print("NO")

node_list = tree.xpath(".//xmlns:node-id", namespaces={'xmlns': 'urn:node-topology'})
for element in tree.iter('{urn:node-topology}node-id'):
    if element in topo:
        # merge
        print("YES")
    else:
        # append
        print("NO")