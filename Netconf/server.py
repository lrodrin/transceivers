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
        print(etree.tostring(tree, encoding='utf8', xml_declaration=True))
        data = util.elm("nc:data")
        data.append(tree)
        util.subelm(data, "node-topology:node", tree)
        self.node_topology = data

    def close(self):
        self.server.close()

    def nc_append_capabilities(self, capabilities):  # pylint: disable=W0613
        util.subelm(capabilities, "capability").text = "urn:ietf:params:netconf:capability:xpath:1.0"
        util.subelm(capabilities, "capability").text = NSMAP["node-topology"]

    def rpc_get_config(self, session, rpc, source_elm, filter_or_none):  # pylint: disable=W0613
        print(etree.tostring(self.node_topology, encoding='utf8', xml_declaration=True))
        return util.filter_results(rpc, self.node_topology, filter_or_none)

    def rpc_edit_config(self, session, rpc, target, data):
        print(etree.tostring(rpc))
        print(etree.tostring(target))
        print(etree.tostring(data))

       
        root_data = etree.XML(etree.tostring(data))
        data_list = root_data.findall(".//xmlns:node", namespaces={'xmlns': 'urn:node-topology'})
        for data in data_list:
          print "HIHI"
          print(data)
          for node_id in data.iter("{urn:node-topology}node-id"):
            print node_id.text

            root_topo = etree.XML(etree.tostring(self.node_topology))
            topo_list = root_topo.findall(".//xmlns:node", namespaces={'xmlns': 'urn:node-topology'})
            
            for topo in topo_list:
              print "HI"
              print(topo)
              for node_id2 in topo.iter("{urn:node-topology}node-id"):
                print node_id2.text
                if node_id.text == node_id2.text:
                  print "MATCH"
        
        
        
        # for he in data_list:
          # for ha in root_topo.iter('{urn:node-topology}node-id'):
            # if he.text == ha.text:
              # print("yes")
            # else:
              #print("fuck the system")   
        
        # check if node-id is in node_topology

        # if yes ==> Check params to modify

        # self.node_topology

        # if no ==> Add it to node_topology

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
