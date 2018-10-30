import argparse
import sys
import time

from netconf import nsmap_add, NSMAP
from netconf import server, util
from pyangbind.lib.serialise import pybindIETFXMLEncoder, pybindIETFXMLDecoder
from lxml import etree
from binding import node_topology
from helpers import *
import pyangbind.lib.pybindJSON as pbJ


import pprint
import binding
import logging
logging.basicConfig(level=logging.DEBUG)

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

nsmap_add("node-topology", "urn:node-topology")


class MyServer(object):
    def __init__(self, username, password, port):
        auth = server.SSHUserPassController(username=username, password=password)
        self.server = server.NetconfSSHServer(server_ctl=auth, server_methods=self, port=port, debug=False)

    def close(self):
        self.server.close()

    def nc_append_capabilities(self, capabilities):  # pylint: disable=W0613
        util.subelm(capabilities, "capability").text = "urn:ietf:params:netconf:capability:xpath:1.0"
        util.subelm(capabilities, "capability").text = NSMAP["node-topology"]

    def rpc_get_config(self, session, rpc, source_elm, filter_or_none):  # pylint: disable=W0613

        print("-"*30)
        #json_root = open('test.json', 'r').read()
        #nodeTopo = pbJ.loads(json_root, binding, "node_topology")
        
        xml_root= open('test.xml', 'r').read()
        nodeTopo = pybindIETFXMLDecoder.decode(xml_root, binding, "node_topology")
        print ("JI")
        xml = pybindIETFXMLEncoder.serialise(nodeTopo)
        print ("JI")

        tree = etree.XML(xml)
        print(etree.tostring(tree))
        data = util.elm("nc:data")
        data.append(tree)
        subdata=util.subelm(data, "node-topology:node", tree )
        print("-"*30)
        print(etree.tostring(data))

        return util.filter_results(rpc, data, filter_or_none)

    def rpc_get(self, session, rpc, filter_or_none):  # pylint: disable=W0613
        """Passed the filter element or None if not present"""

        nt = node_topology()
        nt.node.add("10.1.7.64")
        nt.node.add("10.1.7.65")

        for i, n in nt.node.iteritems():
            n.port.add("1")
            for j, p in n.port.iteritems():
                p.available_core.add("01")

        b = pybindIETFXMLEncoder.serialise(nt)

        data = util.elm("nc:data")
        sysc = util.subelm(data, "node-topology:node")
        x = util.subelm(sysc, b)

        return util.filter_results(rpc, data, filter_or_none, self.server.debug)


def main(*margs):
    parser = argparse.ArgumentParser("Example Netconf Server")
    parser.add_argument("--username", default="admin", help='Netconf username')
    parser.add_argument("--password", default="admin", help='Netconf password')
    parser.add_argument('--port', type=int, default=830, help='Netconf server port')
    args = parser.parse_args(*margs)

    nt = node_topology()
    nt.node.add("10.1.7.64")
    nt.node.add("10.1.7.65")

    for i, n in nt.node.iteritems():
        n.port.add("1")
        for j, p in n.port.iteritems():
            p.available_core.add("01")

    result_xml = pybindIETFXMLEncoder.serialise(nt)
    write_file('node_topology.xml', result_xml)

    s = MyServer(args.username, args.password, args.port)

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
