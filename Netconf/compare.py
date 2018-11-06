from __future__ import print_function

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

root_topo = etree.parse("test.xml").getroot()
root_data = etree.parse("test2.xml").getroot()
topo_list = root_topo.findall(".//xmlns:node-id", namespaces={'xmlns': 'urn:node-topology'})
data_list = root_data.findall(".//xmlns:node-id", namespaces={'xmlns': 'urn:node-topology'})

for data in data_list:
    for topo in topo_list:
        if data.text == topo.text:
            print("MATCH")
        else:
            print("NO MATCH")