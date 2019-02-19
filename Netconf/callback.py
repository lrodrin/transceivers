from __future__ import print_function

import logging

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


# Function to print current configuration
def print_current_config(config):
    logging.debug(etree.tostring(config))


# Function to be called for client of given session whenever configuration changes.
def print_config_changes(config, old_node, new_node, op):
    print("\n ========== CONFIG HAS CHANGED, CURRENT RUNNING CONFIG: ==========\n")
    print_current_config(config)

    new_rows = new_node.xpath("xmlns:port", namespaces={'xmlns': 'urn:node-topology'})

    if old_node is not None:
        print("\n ========== CHANGES: =============================================\n")
        old_rows = old_node.xpath("xmlns:port", namespaces={'xmlns': 'urn:node-topology'})
        print("MODIFIED")
        print("OLD values")
        parse(old_rows, op)
        print("NEW values")
        parse(new_rows, op)
        # changes_list = new_change(old_list, new_list)
        # print("CHANGES", changes_list)

    elif old_node is None:
        print("\n ========== CHANGES: =============================================\n")
        parse(new_rows, op)

    print("\n\n ========== END OF CHANGES =======================================\n")


def caller(callback, args=()):
    callback(*args)
