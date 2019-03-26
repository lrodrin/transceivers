import argparse
import logging
# import subprocess
import sys
import time

from lxml import etree
from netconf import nsmap_add, NSMAP
from netconf import server, util
from pyangbind.lib.serialise import pybindIETFXMLEncoder, pybindIETFXMLDecoder

# from callback import *
import bindingConnection
import bindingTopology
from bindingConnection import node_connectivity

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

logging.basicConfig(level=logging.DEBUG)

nsmap_add("node-topology", "urn:node-topology")
nsmap_add("node-connectivity", "urn:node-connectivity")


class NetconfServer(object):

    def __init__(self, username, password, port):
        auth = server.SSHUserPassController(username=username, password=password)
        self.server = server.NetconfSSHServer(server_ctl=auth, server_methods=self, port=port, debug=False)
        self.node_topology = None
        self.node_connectivity = node_connectivity()

    def close(self):
        self.server.close()

    def load_file(self, filename, module_name):  # load configuration to the servers
        logging.debug("---STARTUP CONFIG---")
        xml_root = open(filename, 'r').read()
        logging.info(etree.tostring(xml_root, encoding='utf8', xml_declaration=True))
        # node_topo = pybindIETFXMLDecoder.decode(xml_root, bindingTopology, module_name)
        # xml = pybindIETFXMLEncoder.serialise(node_topo)
        tree = etree.XML(xml_root)
        logging.info(etree.tostring(tree, encoding='utf8', xml_declaration=True))
        data = util.elm("nc:data")
        data.append(tree)
        logging.info(etree.tostring(data, encoding='utf8', xml_declaration=True))
        self.node_topology = data

    def nc_append_capabilities(self, capabilities):  # pylint: disable=W0613
        logging.debug("---CAPABILITIES---")
        util.subelm(capabilities, "capability").text = "urn:ietf:params:netconf:capability:xpath:1.0"
        util.subelm(capabilities, "capability").text = NSMAP["node-topology"]
        util.subelm(capabilities, "capability").text = NSMAP["node-connectivity"]
        # TODO generalize

    def rpc_get_config(self, session, rpc, source_elm, filter_or_none):  # pylint: disable=W0613
        logging.debug("---GET CONFIG---")
        logging.debug(session)
        # print(etree.tostring(rpc))
        # print(etree.tostring(source_elm))
        # print_current_config(self.configuration)
        # caller(print_current_config, args=self.configuration)
        return util.filter_results(rpc, self.node_topology, filter_or_none)
        # TODO filter_or_none options

    def rpc_edit_config(self, session, rpc, target, method, new_config):  # pylint: disable=W0613
        logging.debug("---EDIT CONFIG---")
        logging.debug(session)
        # print(etree.tostring(rpc))
        # print(etree.tostring(method))
        # print(etree.tostring(new_config))

        # print("RUNNING MONITORING")
        # subprocess.call(['python', 'application_changes.py'])

        if 'topology' in new_config[0].tag:
            topo_path = ".//xmlns:node"
            topo_namespace = 'urn:node-topology'
            data_list = new_config.findall(topo_path, namespaces={'xmlns': topo_namespace})
            for data in data_list:
                found = False
                # print(etree.tostring(data))
                for node_id in data.iter("{" + topo_namespace + "}node-id"):
                    topo_list = self.node_topology.findall(topo_path, namespaces={'xmlns': topo_namespace})
                    for topo in topo_list:
                        # print(etree.tostring(topo))
                        for node_id2 in topo.iter("{" + topo_namespace + "}node-id"):
                            logging.debug("COMPARING %s - %s" % (node_id.text, node_id2.text))
                            if node_id.text == node_id2.text:
                                found = True
                                # aux = copy.deepcopy(topo)  # aux node topology
                                logging.debug("MATCH")
                                logging.debug("MERGING " + node_id.text)
                                merge(topo, data)
                                # print_config_changes(self.configuration, aux, data, 'modify')
                                # caller(print_config_changes, args=(self.configuration, aux, data, 'modify'))
                            else:
                                logging.debug("NOT MATCH")

                    if not found:
                        logging.debug("APPENDING " + node_id.text)
                        self.node_topology[0].append(data)
                        # print_config_changes(self.configuration, None, data, 'create')
                        # caller(print_config_changes, args=(self.configuration, None, data, 'create'))

            # print(etree.tostring(self.configuration, encoding='utf8', xml_declaration=True))
            return util.filter_results(rpc, self.node_topology, None)

        elif 'connectivity' in new_config.tag:
            module_name = 'node-connectivity'
            connid = new_config.find(".//xmlns:connectionid",
                                     namespaces={'xmlns': 'urn:node-connectivity'}).text  # get connectionid

            if method.text == "create":
                logging.debug("CREATING NEW CONNECTION: " + connid)
                if len(self.node_connectivity.connection) == 0:  # if self.capability is empty
                    self.node_connectivity = new_config
                    logging.debug(self.node_connectivity)
                    # encode to pyangbind format
                    self.node_connectivity = pybindIETFXMLDecoder.decode(etree.tostring(self.node_connectivity),
                                                                         bindingConnection,
                                                                         module_name)
                else:
                    if connid not in self.node_connectivity.connection:  # connectionid no exists
                        tree_config = etree.XML(etree.tostring(new_config))
                        # decode from pyangbind format
                        xml = pybindIETFXMLEncoder.serialise(self.node_connectivity)
                        tree_node = etree.XML(xml)
                        tree_node.append(tree_config[0])  # adding new connection
                        # encode to pyangbind format
                        self.node_connectivity = pybindIETFXMLDecoder.decode(etree.tostring(tree_node),
                                                                             bindingConnection,
                                                                             'node-connectivity')
            elif method.text == "delete":
                logging.debug("DELETING CONNECTION: " + connid)
                if connid in self.node_connectivity.connection:  # connectionid exists
                    self.node_connectivity.connection.delete(connid)

            return util.filter_results(rpc, etree.XML(pybindIETFXMLEncoder.serialise(self.node_connectivity)), None)


def merge(one, other):
    """
    This function recursively updates either the text or the children
    of an node if another node is found in `one`, or adds it
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
    parser.add_argument("-username", default="root", help='netconf servers username')
    parser.add_argument("-password", default="netlabN.", help='netconf servers password')
    parser.add_argument('-port', type=int, default=830, help='netconf servers port')
    parser.add_argument('-file', metavar="FILENAME", help='netconf servers configuration file to process')
    parser.add_argument('-model', metavar="YANG MODEL", type=str, default="configuration",
                        help='netconf servers model yang to process')
    args = parser.parse_args(*margs)

    server = NetconfServer(args.username, args.password, args.port)
    server.load_file(args.file, args.model)

    # print("RUNNING MONITORING")
    # subprocess.call(['python', 'application_changes.py'])

    if sys.stdout.isatty():
        print("^C to quit servers")

    # noinspection PyBroadException
    try:
        while True:
            time.sleep(1)

    except Exception:
        print("quitting servers")

    server.close()


if __name__ == "__main__":
    main()
