import argparse
import sys
import time
import socket

from netconf import nsmap_add, NSMAP
from netconf import server, util
from binding import node_topology

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
        """Passed the source element"""

        data = util.elm("nc:data")
        sysc = util.subelm(data, "node-topology:node")
        sysc.append(util.leaf_elm("node-topology:node-id", "10.1.7.64"))

        # Clock
        # clockc = util.subelm(sysc, "sys:clock")
        # tzname = time.tzname[time.localtime().tm_isdst]
        # clockc.append(util.leaf_elm("sys:timezone-utc-offset", int(time.timezone / 100)))

        return util.filter_results(rpc, data, filter_or_none)

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
