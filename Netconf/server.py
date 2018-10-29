import argparse
import sys
import time

from netconf import nsmap_add, NSMAP
from netconf import server, util
from pyangbind.lib.serialise import pybindIETFXMLEncoder
from xml.etree import ElementTree
from binding import node_topology
from helpers import *

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

        # model = node_topology()
        # model.node.add("10.1.7.64")
        
        
        # data = util.elm("nc:data")
        # sysc = util.subelm(data, "node-topology:node")
        # sysc.append(util.leaf_elm("node-topology:node-id", '10.1.7.64'))
        # nose = util.subelm(sysc, "node-topology:port")
        # nose.append(util.leaf_elm("node-topology:port-id", '01'))
        # #
        # # data2 = pybindIETFXMLEncoder.serialise(model)
        # # print(data2)
        # print(ElementTree.tostring(data))

        # nt = node_topology()
        # nt.node.add("10.1.7.64")
        # nt.node.add("10.1.7.65")

        # for i, n in nt.node.iteritems():
        #     n.port.add("1")
        #     for j, p in n.port.iteritems():
        #         p.available_core.add("01")

        # b = pybindIETFXMLEncoder.serialise(nt)
        # print(b)  # xml

        # data = ElementTree.Element("nc:data")
        # data.append(ElementTree.Element(b))
        # print(ElementTree.tostring(data))

        # data = util.elm("nc:data")
        # data.append(util.leaf_elm("node-topology:node", b))
        # print(ElementTree.fromstring(data))

        # return data2

		# nt = node_topology()
		# nt.node.add("10.1.7.64")
		# nt.node.add("10.1.7.65")

		# for i, n in nt.node.iteritems():
		#     n.port.add("1")
		#     for j, p in n.port.iteritems():
		#         p.available_core.add("01")

		# data = pybindIETFXMLEncoder.serialise(nt)
		# # print(data)  # xml

		# write_file('test.xml', data)

		# # tree = ElementTree.parse('test.xml')
		# # root = tree.getroot()
		# # newroot = ElementTree.Element("data")
		# # newroot.insert(0, root)
		# # newroot.append(root)
		# with open('test.xml', 'rb') as f:
		# 	result = f.read()
  #   		print('<nc:data>{}</nc:data>'.format(result))
  #   		t = '<data>{}</data>'.format(result)


        print("-"*30)
        tree = ElementTree.parse('test.xml')
        root = tree.getroot()
        print(ElementTree.tostring(root))
        data = util.elm("nc:data")
        data.append(util.leaf_elm("node-topology:node", ElementTree.tostring(root)))
        print("-"*30)
        print(ElementTree.tostring(data))

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
