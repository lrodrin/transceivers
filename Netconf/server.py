import argparse
# import subprocess
import os
import sys
import time
import logging
import binding
import bindingC

from lxml import etree
from bindingC import node_connectivity
from netconf import nsmap_add, NSMAP
from netconf import server, util
from pyangbind.lib.serialise import pybindIETFXMLEncoder, pybindIETFXMLDecoder

from helpers import *

# from callback import *

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

logging.basicConfig(level=logging.DEBUG)

nsmap_add("node-topology", "urn:node-topology")
nsmap_add("node-connectivity", "urn:node-connectivity")


class MyServer(object):

    def __init__(self, username, password, port):
        auth = server.SSHUserPassController(username=username, password=password)
        self.server = server.NetconfSSHServer(server_ctl=auth, server_methods=self, port=port, debug=False)
        self.node_topology = None
        self.node_connectivity = node_connectivity()

    def close(self):
        self.server.close()

    def load_file(self, filename, module_name):  # load configuration to the server
        logging.debug("--LOAD FILE--")
        xml_root = open(filename, 'r').read()
        node_topo = pybindIETFXMLDecoder.decode(xml_root, binding, module_name)
        xml = pybindIETFXMLEncoder.serialise(node_topo)
        tree = etree.XML(xml)
        # print(etree.tostring(tree, encoding='utf8', xml_declaration=True))
        data = util.elm("nc:data")
        data.append(tree)
        print(etree.tostring(data, encoding='utf8', xml_declaration=True))
        self.node_topology = data

    def nc_append_capabilities(self, capabilities):  # pylint: disable=W0613
        logging.debug("--APPEND CAPABILITIES--")
        util.subelm(capabilities, "capability").text = "urn:ietf:params:netconf:capability:xpath:1.0"
        util.subelm(capabilities, "capability").text = NSMAP["node-topology"]
        util.subelm(capabilities, "capability").text = NSMAP["node-connectivity"]
        # TODO generalize

    def rpc_get_config(self, session, rpc, source_elm, filter_or_none):  # pylint: disable=W0613
        logging.debug("--GET CONFIG--")
        logging.debug(session)
        print(etree.tostring(rpc))
        print(etree.tostring(source_elm))
        # print_current_config(self.node_topology)
        # caller(print_current_config, args=self.node_topology)
        return util.filter_results(rpc, self.node_topology, filter_or_none)
        # TODO filter_or_none options

    def rpc_edit_config(self, session, rpc, target, method, new_config):  # pylint: disable=W0613
        logging.debug("--EDIT CONFIG--")
        logging.debug(session)
        # print(etree.tostring(rpc))
        # print(etree.tostring(target))
        print(etree.tostring(method))
        print(etree.tostring(new_config))

        # print("RUNNING MONITORING")
        # subprocess.call(['python', 'application_changes.py'])

        if 'topology' in new_config[0].tag:
            topo_path = ".//xmlns:node"
            topo_namespace = 'urn:node-topology'
            data_list = new_config.findall(topo_path, namespaces={'xmlns': topo_namespace})
            for data in data_list:
                found = False
                # print(etree.tostring(data))
                # for node_id in data.iter("{urn:node-topology}node-id"):
                for node_id in data.iter("{" + topo_namespace + "}node-id"):
                    topo_list = self.node_topology.findall(topo_path, namespaces={'xmlns': topo_namespace})
                    for topo in topo_list:
                        # print(etree.tostring(topo))
                        # for node_id2 in topo.iter("{urn:node-topology}node-id"):
                        for node_id2 in topo.iter("{" + topo_namespace + "}node-id"):
                            logging.debug("%s - %s" % (node_id.text, node_id2.text))
                            if node_id.text == node_id2.text:
                                found = True
                                logging.debug("MATCH")
                                # aux = copy.deepcopy(topo)  # aux node topology
                                logging.debug("MERGING " + node_id.text)
                                merge(topo, data)
                                # print_config_changes(self.node_topology, aux, data, 'modify')
                                # caller(print_config_changes, args=(self.node_topology, aux, data, 'modify'))
                            else:
                                logging.debug("NOT MATCH")

                    if not found:
                        logging.debug("APPENDING " + node_id.text)
                        self.node_topology[0].append(data)
                        # print_config_changes(self.node_topology, None, data, 'create')
                        # caller(print_config_changes, args=(self.node_topology, None, data, 'create'))

            # print(etree.tostring(self.node_topology, encoding='utf8', xml_declaration=True))
            return util.filter_results(rpc, self.node_topology, None)

        elif 'connectivity' in new_config.tag:
            module_name = 'node-connectivity'
            connid = new_config.find(".//xmlns:connectionid",
                                     namespaces={'xmlns': 'urn:node-connectivity'}).text  # get connectionid

            if method.text == "create":
                print("NEW CONNECTION " + connid)
                if len(self.node_connectivity.connection) == 0:  # if self.node_connectivity is empty
                    self.node_connectivity = new_config
                    # encode to pyangbind format
                    self.node_connectivity = pybindIETFXMLDecoder.decode(etree.tostring(self.node_connectivity),
                                                                         bindingC,
                                                                         module_name)

                else:
                    if connid not in self.node_connectivity.connection:  # connectionid no exists
                        tree_config = etree.XML(etree.tostring(new_config))
                        # decode from pyangbind format
                        xml = pybindIETFXMLEncoder.serialise(self.node_connectivity)
                        tree_node = etree.XML(xml)
                        tree_node.append(tree_config[0])  # adding new connection

                        # encode to pyangbind format
                        self.node_connectivity = pybindIETFXMLDecoder.decode(etree.tostring(tree_node), bindingC,
                                                                             'node-connectivity')
            elif method.text == "delete":
                if connid in self.node_connectivity.connection:  # connectionid exists
                    print("DELETE CONNECTION " + connid)
                    self.node_connectivity.connection.delete(connid)

            return util.filter_results(rpc, etree.XML(pybindIETFXMLEncoder.serialise(self.node_connectivity)), None)


def merge(one, other):
    """
    This function recursively updates either the text or the children
    of an element if another element is found in `one`, or adds it
    from `other` if not found.
    """
    # Create a mapping from tag name to element, as that's what we are filtering with
    mapping = {el.tag: el for el in one}
    for el in other:
        if len(el) == 0:
            # Not nested
            try:
                # Update the text
                mapping[el.tag].text = el.text

            except KeyError:
                # An element with this name is not in the mapping
                mapping[el.tag] = el
                # Add it
                one.append(el)
        else:

            try:
                # Recursively process the element, and update it in the same way
                merge(mapping[el.tag], el)

            except KeyError:
                # Not in the mapping
                mapping[el.tag] = el
                # Just add it
                one.append(el)

    return etree.tostring(one)


def main(*margs):
    parser = argparse.ArgumentParser("Example Netconf Server")
    parser.add_argument("-username", default="root", help='netconf server username')
    parser.add_argument("-password", default="netlabN.", help='netconf server password')
    parser.add_argument('-port', type=int, default=830, help='netconf server port')
    parser.add_argument('-file', metavar="FILENAME", help='netconf server configuration file to process')
    parser.add_argument('-model', metavar="YANG MODEL", type=str, default="node_topology",
                        help='netconf server model yang to process')
    args = parser.parse_args(*margs)

    s = MyServer(args.username, args.password, args.port)
    s.load_file(args.file, args.model)

    # print("RUNNING MONITORING")
    # subprocess.call(['python', 'application_changes.py'])

    if sys.stdout.isatty():
        print("^C to quit server")

    # noinspection PyBroadException
    try:
        while True:
            time.sleep(1)

    except Exception:
        print("quitting server")

    s.close()


if __name__ == "__main__":
    main()
