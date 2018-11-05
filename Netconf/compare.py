import xml.etree.ElementTree as ET

from lxml import etree

tree = etree.parse('test.xml')
# tree = ET.parse('items.xml')
root = tree.getroot()

# find all "item" objects and print their "name" attribute
for elem in root:
    for subelem in elem.findall(".//xmlns:node-id", namespaces={'xmlns': 'urn:node-topology'}):

        # if we don't need to know the name of the attribute(s), get the dict
        print(subelem.text)

        # if we know the name of the attribute, access it directly
        print(subelem.get('node-id'))

for k, v in root.items():
    print(k, v)