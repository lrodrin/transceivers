from __future__ import print_function

from lxml import etree
from netconf import util
root_data = etree.parse("test2.xml")
data_list = root_data.findall(".//xmlns:node", namespaces={'xmlns': 'urn:node-topology'})
for data in data_list:
    # print(data)
    for node_id in data.iter("{urn:node-topology}node-id"):
        # print(node_id.text)
        allowed_names = []
        root_topo = etree.parse("test.xml")
        topo_list = root_topo.findall(".//xmlns:node", namespaces={'xmlns': 'urn:node-topology'})

        for topo in topo_list:
            # print(topo)
            for node_id2 in topo.iter("{urn:node-topology}node-id"):
                allowed_names.append(node_id2.text)
                print("%s - %s" % (node_id.text, node_id2.text))
                if node_id.text == node_id2.text:
                    print("MATCH")
                    print(etree.tostring(node_id))
                    print(etree.tostring(topo))
                    print("MATCH")
                else:
                    print("NO MATCH")
                    # print(etree.tostring(data))
print(allowed_names)


# root_topo = etree.parse("test.xml")
# root_data = etree.parse("test2.xml")
#
# parent = root_topo.find(".//xmlns:node", namespaces={'xmlns': 'urn:node-topology'})
# print(parent.tag)
#
# new_condition = root_data.getroot()
# parent.append(new_condition)
# print(etree.tostring(root_topo))