import argparse
import subprocess
import sys
import time
import copy
import binding

from netconf import nsmap_add, NSMAP
from netconf import server, util
from pyangbind.lib.serialise import pybindIETFXMLEncoder, pybindIETFXMLDecoder

# from helpers import *
from callback import *

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

logging.basicConfig(level=logging.DEBUG)
nsmap_add("node-topology", "urn:node-topology")


class MyServer(object):

    def __init__(self, username, password, port):
        auth = server.SSHUserPassController(username=username, password=password)
        self.server = server.NetconfSSHServer(server_ctl=auth, server_methods=self, port=port, debug=False)
        self.node_topology = None

    def load_file(self, filename):  # load configuration to the server
        xml_root = open(filename, 'r').read()
        node_topo = pybindIETFXMLDecoder.decode(xml_root, binding, "node_topology")
        xml = pybindIETFXMLEncoder.serialise(node_topo)
        tree = etree.XML(xml)
        # print(etree.tostring(tree, encoding='utf8', xml_declaration=True))
        data = util.elm("nc:data")
        data.append(tree)
        # print(etree.tostring(data, encoding='utf8', xml_declaration=True))
        self.node_topology = data

    def nc_append_capabilities(self, capabilities):  # pylint: disable=W0613
        util.subelm(capabilities, "capability").text = "urn:ietf:params:netconf:capability:xpath:1.0"
        util.subelm(capabilities, "capability").text = NSMAP["node-topology"]
        # TODO generalize

    def rpc_get_config(self, session, rpc, source_elm, filter_or_none):  # pylint: disable=W0613
        logging.debug("--GET CONFIG--")
        logging.debug(session)
        # print(etree.tostring(rpc))
        # print(etree.tostring(source_elm))
        # print_current_config(self.node_topology)
        caller(print_current_config, args=self.node_topology)
        # logging.debug(etree.tostring(self.node_topology, encoding='utf8', xml_declaration=True))
        return util.filter_results(rpc, self.node_topology, filter_or_none)
        # TODO filter_or_none options

    def rpc_edit_config(self, session, rpc, target, new_config):
        logging.debug("--EDIT CONFIG--")
        logging.debug(session)
        # print(etree.tostring(rpc))
        # print(etree.tostring(target))
        # print(etree.tostring(new_config))

        # print("RUNNING MONITORING")
        # subprocess.call(['python', 'application_changes.py'])
        # old_topology = copy.deepcopy(self.node_topology)
        # print(etree.tostring(old_topology))

        data_list = new_config.findall(".//xmlns:node", namespaces={'xmlns': 'urn:node-topology'})
        for data in data_list:
            found = False
            # print(etree.tostring(data))
            for node_id in data.iter("{urn:node-topology}node-id"):
                topo_list = self.node_topology.findall(".//xmlns:node", namespaces={'xmlns': 'urn:node-topology'})
                for topo in topo_list:
                    # print(etree.tostring(topo))
                    for node_id2 in topo.iter("{urn:node-topology}node-id"):
                        logging.debug("%s - %s" % (node_id.text, node_id2.text))
                        if node_id.text == node_id2.text:
                            found = True
                            logging.debug("MATCH")
                            aux = copy.deepcopy(topo)  # aux node topology
                            logging.debug("MERGING " + node_id.text)
                            merge(topo, data)
                            # print_config_changes(self.node_topology, aux, data, 'modify')
                            caller(print_config_changes, args=(self.node_topology, aux, data, 'modify'))
                        else:
                            logging.debug("NOT MATCH")

                if not found:
                    logging.debug("APPENDING " + node_id.text)
                    self.node_topology[0].append(data)
                    # print_config_changes(self.node_topology, None, data, 'create')
                    caller(print_config_changes, args=(self.node_topology, None, data, 'create'))

        # print(etree.tostring(self.node_topology, encoding='utf8', xml_declaration=True))
        return util.filter_results(rpc, self.node_topology, None)

    # def rpc_get(self, session, rpc, filter_or_none):
    # logging.debug("--GET--")
    # logging.debug(session)
    # print(etree.tostring(rpc))
    # print(etree.tostring(source_elm))
    # print_current_config(self.node_topology)
    # caller(print_current_config, args=self.node_topology)
    # logging.debug(etree.tostring(self.node_topology, encoding='utf8', xml_declaration=True))
    # return util.filter_results(rpc, self.node_topology, filter_or_none)
    # TODO filter_or_none options

    def close(self):
        self.server.close()

    # def write_xml(self):  # create an xml example with binding
    #     node_topo = binding.node_topology()
    #     node_topo.node.add("10.1.7.64")
    #     node_topo.node.add("10.1.7.65")
    #
    #     for i, n in node_topo.node.iteritems():
    #         n.port.add('1')
    #         for j, p in n.port.iteritems():
    #             p.available_core.add('1')
    #
    #     result_xml = pybindIETFXMLEncoder.serialise(node_topo)
    #     write_file('node_topology.xml', result_xml)


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
    parser.add_argument("--username", default="admin", help='Netconf username')
    parser.add_argument("--password", default="admin", help='Netconf password')
    parser.add_argument('--port', type=int, default=830, help='Netconf port')
    args = parser.parse_args(*margs)

    s = MyServer(args.username, args.password, args.port)
    s.load_file('test.xml')

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
