import io

from lxml import etree

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

# root_1 = etree.parse('test.xml').getroot()
# root_2 = etree.parse('test3.xml').getroot()

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

# old_topo = root_1.xpath("///xmlns:node-id/text()", namespaces={'xmlns': 'urn:node-topology'})
# print(old_topo)
# new_topo = root_2.findall(".//xmlns:node", namespaces={'xmlns': 'urn:node-topology'})
# print(new_topo)
#
# for node in new_topo:
#     for node_id in node.iter("{urn:node-topology}node-id"):
#         print("%s" % node_id.text)
#         if node_id.text not in old_topo:
#             print("CREATED")
#             print(etree.tostring(node))
#         else:
#             print("MODIFIED")
#             print("NOT MODIFIED")


# recorrer els dos nodes i veure les diferencies + parsejar
# recorrer un node i parsejar

def parse(ports):
    all_data = []
    for port in ports:
        d = {}
        for elem in port.iter():
            if '\n' not in elem.text:
                aux = elem.tag.replace('{urn:node-topology}', '')
                d[aux] = elem.text
        all_data.append(d)
    return all_data


def new_change(old_list, new_list):
    change_list = []
    for x in new_list:
        for y in old_list:
            if x['port-id'] == y['port-id']:
                change_list.append(x)
    return change_list


if __name__ == '__main__':
    root_1 = etree.parse('node1.xml')
    # rows_1 = root_1.xpath('port')
    rows_1 = root_1.xpath("xmlns:port", namespaces={'xmlns': 'urn:node-topology'})
    root_2 = etree.parse('node2.xml')
    rows_2 = root_2.xpath("xmlns:port", namespaces={'xmlns': 'urn:node-topology'})
    print("OLD", parse(rows_1))
    print("NEW", parse(rows_2))

    old_ist = parse(rows_1)
    new_list = parse(rows_2)
    print("CHANGES", new_change(old_ist, new_list))

    find_text = etree.XPath("//text()")
    for text in find_text(root_1):
        if '\n' not in text:
            print(root_1.getpath(text.getparent()))

