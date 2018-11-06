import xml.etree.ElementTree as ET

from lxml import etree

# tree = etree.parse('test.xml ')
# tree = ET.parse('items.xml')
# root = tree.getroot()

# for elem in root:
#     for subelem in elem.findall(".//xmlns:node-id", namespaces={'xmlns': 'urn:node-topology'}):
#
#         # if we don't need to know the name of the attribute(s), get the dict
#         print(subelem.text)
#
#         # if we know the name of the attribute, access it directly
#         print(subelem.get('node-id'))
#
# for k, v in root.items():
#     print(k, v)
# find all "item" objects and print their "name" attribute

data = []

tree = etree.parse("test.xml")
root = tree.getroot()
tree_2 = etree.parse("test2.xml")
root_2 = tree_2.getroot()

server_list = root.xpath(".//xmlns:node-id", namespaces={'xmlns': 'urn:node-topology'})
client_list = root_2.xpath(".//xmlns:node-id", namespaces={'xmlns': 'urn:node-topology'})

for nodeS in server_list:
    print(nodeS.text)

print('-'*10)

for nodeC in client_list:
    print(nodeC.text)