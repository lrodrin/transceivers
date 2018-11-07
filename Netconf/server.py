import argparse
import sys
import time
import binding
import logging

from netconf import nsmap_add, NSMAP
from netconf import server, util
from pyangbind.lib.serialise import pybindIETFXMLEncoder, pybindIETFXMLDecoder
from lxml import etree
from helpers import *

logging.basicConfig(level=logging.DEBUG)

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

nsmap_add("node-topology", "urn:node-topology")


class MyServer(object):

    def __init__(self, username, password, port):
        auth = server.SSHUserPassController(username=username, password=password)
        self.server = server.NetconfSSHServer(server_ctl=auth, server_methods=self, port=port, debug=False)
        self.node_topology = None

    def load_file(self):
        xml_root = open('test.xml', 'r').read()
        node_topo = pybindIETFXMLDecoder.decode(xml_root, binding, "node_topology")
        xml = pybindIETFXMLEncoder.serialise(node_topo)
        tree = etree.XML(xml)
        # print(etree.tostring(tree, encoding='utf8', xml_declaration=True))
        data = util.elm("nc:data")
        data.append(tree)
        self.node_topology = data

    def close(self):
        self.server.close()

    def nc_append_capabilities(self, capabilities):  # pylint: disable=W0613
        util.subelm(capabilities, "capability").text = "urn:ietf:params:netconf:capability:xpath:1.0"
        util.subelm(capabilities, "capability").text = NSMAP["node-topology"]

    def rpc_get_config(self, session, rpc, source_elm, filter_or_none):  # pylint: disable=W0613
        print(etree.tostring(self.node_topology, encoding='utf8', xml_declaration=True))
        return util.filter_results(rpc, self.node_topology, filter_or_none)

    def rpc_edit_config(self, session, rpc, target, new_config):
        # print(etree.tostring(rpc))
        # print(etree.tostring(target))
        # print(etree.tostring(new_config))

        # print(new_config)
        data_list = new_config.findall(".//xmlns:node", namespaces={'xmlns': 'urn:node-topology'})
        for data in data_list:
            found = False
            # print(data)
            for node_id in data.iter("{urn:node-topology}node-id"):

                topo_list = self.node_topology.findall(".//xmlns:node", namespaces={'xmlns': 'urn:node-topology'})

                for topo in topo_list:
                    # print(topo)
                    for node_id2 in topo.iter("{urn:node-topology}node-id"):
                        print("%s - %s" % (node_id.text, node_id2.text))
                        # print("%s %s" % (etree.tostring(topo), etree.tostring(data)))
                        if node_id.text == node_id2.text:
                            print "MATCH"
                            found = True
                        else:
                            print("NO MATCH")
                print(found)
                if not found:
                    print("NOT FOUND. APPENDING " + node_id.text)
                    self.node_topology[0].append(data)
                elif found:
                    pass

        #        print("OPTIMITZATION")
        #        t_list = self.node_topology.xpath("///xmlns:node-id/text()", namespaces={'xmlns': 'urn:node-topology'})

        #        for data in data_list:
        #          for node_id in data.iter("{urn:node-topology}node-id"):
        #            print("%s - %s" % (node_id.text, t_list))
        #            if node_id.text in t_list:
        #              print("MATCH")
        #            else:
        #              print("NO MATCH")
        #              self.node_topology[0].append(data)

        print(etree.tostring(self.node_topology, encoding='utf8', xml_declaration=True))
        return util.filter_results(rpc, self.node_topology, None)

    #  def rpc_get(self, ):
    #      return util.filter_results(rpc, self.node_topology, filter_or_none)

    # create an xml example
    def write_xml(self):
        nt = binding.node_topology()  # create server configuration
        nt.node.add("10.1.7.64")
        nt.node.add("10.1.7.65")

        for i, n in nt.node.iteritems():
            n.port.add("1")
            for j, p in n.port.iteritems():
                p.available_core.add("01")

        result_xml = pybindIETFXMLEncoder.serialise(nt)
        write_file('node_topology.xml', result_xml)


def main(*margs):
    parser = argparse.ArgumentParser("Example Netconf Server")
    parser.add_argument("--username", default="admin", help='Netconf username')
    parser.add_argument("--password", default="admin", help='Netconf password')
    parser.add_argument('--port', type=int, default=830, help='Netconf server port')
    args = parser.parse_args(*margs)

    s = MyServer(args.username, args.password, args.port)
    s.load_file()

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
