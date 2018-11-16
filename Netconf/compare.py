from __future__ import print_function

from lxml import etree

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"


def get_ancestors(aux, elem):
    # print(elem, aux)
    ancestors_list = [aux]
    for ancestor in elem.iterancestors():
        ancestors_list.append(ancestor.tag.replace('{urn:node-topology}', ''))
        # print(ancestor.tag.replace('{urn:node-topology}', ''), end=" ")

    # print(ancestors_list[::-1])
    return ancestors_list[::-1]


def pretty_print(aux, elem, operation):
    tag_list = get_ancestors(aux, elem)
    # print(tag_list)
    if operation == 'create':
        print("CREATED: ", end=' ')
        print("/".join(tag_list), end=' ')
    elif operation == 'modify':
        print("MODIFIED: ", end=' ')
        print("/".join(tag_list), end=' ')
    print("=", elem.text)


def parse(rows, operation):
    all_data = []
    for row in rows:
        d = {}
        for elem in row.iter():
            if '\n' not in elem.text:
                aux = elem.tag.replace('{urn:node-topology}', '')
                d[aux] = elem.text
                pretty_print(aux, elem, operation)
        all_data.append(d)

    return all_data


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
    old_list = parse(rows_1, 'create')
    new_list = parse(rows_2, 'create')
    print("OLD values", old_list)
    print("NEW values", new_list)
    print("CHANGES", new_change(old_list, new_list))

    print("\n---EXAMPLE MODIFY---")
    old_list = parse(rows_1, 'modify')
    new_list = parse(rows_2, 'modify')
    print("OLD values", old_list)
    print("NEW values", new_list)
    print("CHANGES", new_change(old_list, new_list))
