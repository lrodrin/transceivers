import argparse
import sys
import time
import copy
import binding

from netconf import nsmap_add, NSMAP
from netconf import server, util
from pyangbind.lib.serialise import pybindIETFXMLEncoder, pybindIETFXMLDecoder
from callback import *
from combine import *

logging.basicConfig(level=logging.DEBUG)

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

nsmap_add("node-topology", "urn:node-topology")


class MyServer(object):

    def __init__(self, username, password, port):
        auth = server.SSHUserPassController(username=username, password=password)
        self.server = server.NetconfSSHServer(server_ctl=auth, server_methods=self, port=port, debug=False)
        self.node_topology = None

    def load_file(self, filename):  # create configuration
        xml_root = open(filename, 'r').read()
        node_topo = pybindIETFXMLDecoder.decode(xml_root, binding, "node_topology")
        xml = pybindIETFXMLEncoder.serialise(node_topo)
        tree = etree.XML(xml)
        # print(etree.tostring(tree, encoding='utf8', xml_declaration=True))
        # logging.debug(etree.tostring(tree, encoding='utf8', xml_declaration=True))
        data = util.elm("nc:data")
        data.append(tree)
        # print(etree.tostring(data, encoding='utf8', xml_declaration=True))
        # logging.debug(etree.tostring(data, encoding='utf8', xml_declaration=True))
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

        print_current_config(etree.tostring(self.node_topology))
        logging.debug(etree.tostring(self.node_topology, encoding='utf8', xml_declaration=True))
        return util.filter_results(rpc, self.node_topology, filter_or_none)
        # TODO filter_or_none options

    def rpc_edit_config(self, session, rpc, target, new_config):
        logging.debug("--EDIT CONFIG--")
        logging.debug(session)
        # print(etree.tostring(rpc))
        # print(etree.tostring(target))
        # print(etree.tostring(new_config))
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
                        # print("%s - %s" % (node_id.text, node_id2.text))
                        if node_id.text == node_id2.text:
                            logging.debug("MATCH")
                            found = True
                            aux = topo  # current node topology
                            # call(etree.tostring(aux), nse)
                            logging.debug("MERGING " + node_id.text)
                            # print("OLD", etree.tostring(aux))
                            # print("NEW", etree.tostring(data))
                            comb(aux, data)
                            # print("HOLA")
                            # print(etree.tostring(aux))
                            # print(etree.tostring(data))
                            # call(etree.tostring(aux), nse)

                        else:
                            logging.debug("NOT MATCH")

                if not found:
                    logging.debug("APPENDING " + node_id.text)
                    self.node_topology[0].append(data)

        # caller(etree.tostring(old_topology), etree.tostring(self.node_topology), get_changes)
        logging.debug(etree.tostring(self.node_topology, encoding='utf8', xml_declaration=True))
        return util.filter_results(rpc, self.node_topology, None)

    # def rpc_get(self, session, rpc, filter_or_none):
    #     logging.debug("--GET--")
    #     logging.debug(session)
    #     print(etree.tostring(rpc))
    #     print(etree.tostring(source_elm))

    #     print_current_config(etree.tostring(self.node_topology))
    #     logging.debug(etree.tostring(self.node_topology, encoding='utf8', xml_declaration=True))
    #     return util.filter_results(rpc, self.node_topology, filter_or_none)
    #     TODO filter_or_none options

    def close(self):
        self.server.close()

    # create an xml example
    # def write_xml(self):
    #     nt = binding.node_topology()
    #     nt.node.add("10.1.7.64")
    #     nt.node.add("10.1.7.65")

    #     for i, n in nt.node.iteritems():
    #         n.port.add("1")
    #         for j, p in n.port.iteritems():
    #             p.available_core.add("01")

    #     result_xml = pybindIETFXMLEncoder.serialise(nt)
    #     write_file('node_topology.xml', result_xml)


def main(*margs):
    parser = argparse.ArgumentParser("Example Netconf Server")
    parser.add_argument("--username", default="admin", help='Netconf username')
    parser.add_argument("--password", default="admin", help='Netconf password')
    parser.add_argument('--port', type=int, default=830, help='Netconf server port')
    args = parser.parse_args(*margs)

    s = MyServer(args.username, args.password, args.port)
    s.load_file('test.xml')

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
