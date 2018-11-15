from __future__ import print_function

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
                # aux = elem.tag
                d[aux] = elem.text
                # print(elem.getroottree().getpath(elem) + " = " + elem.text)
                print("HOOOOOOOOOOOOOOOOLAAAAAAAAAAAAAAAAAA")
                print(aux)
                print(elem)
                tag_list = get_ancestors(aux, elem)
                print("/".join(tag_list), end=' ')
                print("=", elem.text)


        all_data.append(d)
    return all_data


def get_ancestors(aux, elem):
    ancestors_list = list()
    # print(elem.text, aux, end=" ")
    ancestors_list.append(aux)
    for ancestor in elem.iterancestors():
        ancestors_list.append(ancestor.tag.replace('{urn:node-topology}', ''))
        # print(ancestor.tag.replace('{urn:node-topology}', ''), end=" ")
    # print()
    # print(ancestors_list[::-1], end=' ')
    return ancestors_list[::-1]


def new_change(old_list, new_list):
    change_list = []
    for x in new_list:
        for y in old_list:
            if x['port-id'] == y['port-id']:
                change_list.append(x)
    return change_list


if __name__ == '__main__':
    root_1 = etree.parse('node1.xml').getroot()
    root_2 = etree.parse('node2.xml').getroot()
    rows_1 = root_1.xpath("xmlns:port", namespaces={'xmlns': 'urn:node-topology'})  # ports list
    rows_2 = root_2.xpath("xmlns:port", namespaces={'xmlns': 'urn:node-topology'})
    # rows_1 = root_1.xpath("port")
    # rows_2 = root_2.xpath("port")
    print("OLD", parse(rows_1))
    print("NEW", parse(rows_2))

    old_ist = parse(rows_1)
    new_list = parse(rows_2)
    print("CHANGES", new_change(old_ist, new_list))



