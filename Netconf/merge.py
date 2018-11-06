from __future__ import print_function
from lxml import etree

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"


# print(tree.xpath(".//xmlns:node-id", namespaces={'xmlns': 'urn:node-topology'}))

# topo = tree.xpath(".//xmlns:node-id", namespaces={'xmlns': 'urn:node-topology'})

# for elem in topo:
#     print(elem.text)
#
# print("-"*10)

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

# server configuration
server = etree.parse('test.xml').getroot()
#print(etree.tostring(server, encoding='utf8', xml_declaration=True))

# client configuration
client = etree.parse('test2.xml').getroot()
#print(etree.tostring(client, encoding='utf8', xml_declaration=True))

output = open('merge.xml','w')
xml_element_tree = None
for node in client.iter('{urn:node-topology}node-id'):
    if xml_element_tree is None:
        xml_element_tree = client
        insertion_point = xml_element_tree.findall(".//node-id/*")
    else:
        insertion_point.extend(node)
    # node_list = client.xpath(".//xmlns:node-id", namespaces={'xmlns': 'urn:node-topology'})
if xml_element_tree is not None:
    print(etree.tostring(xml_element_tree))
#
# ns = {'merda': 'urn:node-topology'}
#
# for node in client.findall('.//merda:node-id', ns):
#     id = server.find('.//merda:node-id', ns)
#     print(id.text)

root = etree.parse('test.xml')
rows = root.findall("./xmlns:node", namespaces={'xmlns': 'urn:node-topology'})

all_data = []

for row in rows:
    field_dict = {}
    fields = row.findall(".//xmlns:node-id", namespaces={'xmlns': 'urn:node-topology'})

    for field in fields:
        field_dict['node-id'] = field.text

    # print(field_dict)

    all_data.append(field_dict)

print(all_data)