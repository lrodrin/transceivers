from __future__ import print_function

from lxml import etree

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"


def get_ancestors(aux, elem):
    # print(elem, aux)
    ancestors_list = [aux]
    for ancestor in elem.iterancestors():
        # ancestor.tag.replace('{urn:node-topology}', '')
        if ancestor.tag.replace('{urn:node-topology}', '') == 'node':
            node_id = ancestor.find("xmlns:node-id", namespaces={'xmlns': 'urn:node-topology'}).text
            ancestors_list.append(node_id)

        ancestors_list.append(ancestor.tag)

        # print(ancestor.tag.replace('{urn:node-topology}', ''), end=" ")

    # print(ancestors_list[::-1])
    return ancestors_list[::-1]


def parse(rows, op):
    # all_data = []
    for row in rows:
        d = {}
        for elem in row.iter():
            if '\n' not in elem.text:
                # aux = elem.tag.replace('{urn:node-topology}', '')
                aux = elem.tag
                d[aux] = elem.text
                tag_list = get_ancestors(aux, elem)
                # print(tag_list)
                if op == 'create':
                    print("CREATED: /", end='')
                    print("/".join(tag_list[2:]).replace('{urn:node-topology}', ''), end=' ')
                elif op == 'modify':
                    if any("{urn:ietf:params:xml:ns:netconf:base:1.0}" in s for s in tag_list):
                        print("/", end='')
                        print("/".join(tag_list[3:]).replace('{urn:node-topology}', ''), end=' ')
                    else:
                        print("/node-topology/", end='')  # TODO pass yang model
                        print("/".join(tag_list).replace('{urn:node-topology}', ''), end=' ')

                print("=", elem.text)

        # all_data.append(d)

    # return all_data


def new_change(old_values, new_values):
    change_list = []
    for x in new_values:
        for y in old_values:
            if x['port-id'] == y['port-id']:
                change_list.append(x)

    return change_list


if __name__ == '__main__':
    root_1 = etree.parse('node1.xml').getroot()
    root_2 = etree.parse('node2.xml').getroot()
    rows_1 = root_1.xpath("xmlns:port", namespaces={'xmlns': 'urn:node-topology'})
    rows_2 = root_2.xpath("xmlns:port", namespaces={'xmlns': 'urn:node-topology'})

    print("---EXAMPLE CREATE---")
    # new_list = parse(rows_2, 'create')
    # print("NEW values",new_list)
    parse(rows_2, 'create')

    print("\n---EXAMPLE MODIFY---")
    operation = 'modify'
    # old_list = parse(rows_1, operation)
    # new_list = parse(rows_2, operation)
    # print("OLD values", old_list)
    # print("NEW values", new_list)
    print("MODIFIED")
    print("OLD values")
    parse(rows_1, operation)
    print("NEW values")
    parse(rows_2, operation)
    # changes_list = new_change(old_list, new_list)
    # print("CHANGES", changes_list)
