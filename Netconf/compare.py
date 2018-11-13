from lxml import etree

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

root_1 = etree.parse('test.xml').getroot()
root_2 = etree.parse('test3.xml').getroot()

old = root_1.findall('node')

node_list = root_1.xpath("///node-id/text()")
print(node_list)

all_data = []

i = 0
j = 0
for o in old:
    field_dict = {}
    new = root_2.findall('node')
    for n in new:
        # print(n[0].text)
        if n[0].text == o[0].text:
            print("OLD" + str(i) + str(j) + etree.tostring(o))
            print("NEW" + str(i) + str(j) + etree.tostring(n))
        j += 1
    i += 1
    print(field_dict)

    all_data.append(field_dict)

print(all_data)

old_topo = root_1.xpath("///node-id/text()")
new_topo = root_2.findall(".//node")

for node in new_topo:
    for node_id in node.iter("node-id"):
        print("%s" % node_id.text)
        if node_id.text not in old_topo:
            print("CREATED")
            print(node)
        else:
            print("MODIFIED")
            print("NOT MODIFIED")
