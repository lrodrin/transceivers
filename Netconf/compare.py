import io

from lxml import etree

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

root_1 = etree.parse('test.xml').getroot()
root_2 = etree.parse('test3.xml').getroot()

# old = root_1.findall('node')
#
# node_list = root_1.xpath("///node-id/text()")
# print(node_list)
#
# all_data = []
#
# i = 0
# j = 0
# for o in old:
#     field_dict = {}
#     new = root_2.findall('node')
#     for n in new:
#         # print(n[0].text)
#         if n[0].text == o[0].text:
#             print("OLD" + str(i) + str(j) + etree.tostring(o))
#             print("NEW" + str(i) + str(j) + etree.tostring(n))
#         j += 1
#     i += 1
#     print(field_dict)
#
#     all_data.append(field_dict)
#
# print(all_data)

old_topo = root_1.xpath("///xmlns:node-id/text()", namespaces={'xmlns': 'urn:node-topology'})
print(old_topo)
new_topo = root_2.findall(".//xmlns:node", namespaces={'xmlns': 'urn:node-topology'})
print(new_topo)

for node in new_topo:
    for node_id in node.iter("{urn:node-topology}node-id"):
        print("%s" % node_id.text)
        if node_id.text not in old_topo:
            print("CREATED")
            print(etree.tostring(node))
        else:
            print("MODIFIED")
            print("NOT MODIFIED")

print("HOLA")
# recorrer els dos nodes i veure les diferencies + parsejar
# recorrer un node i parsejar