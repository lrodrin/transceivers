import argparse
import sys

from ncclient import manager
from defaults import *
from helpers import *

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"


def edit_config(xml, host, port, user, pwd):
    with manager.connect(host=host, port=port, username=user, password=pwd,
                         hostkey_verify=False, device_params={'name': 'default'}) as m:
        reply = m.edit_config(target='running', config=xml)
    return reply


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--topology', '-t', default=XML, help="XML Topology configuration file")
    parser.add_argument('--host', '-H', default=HOST, help="remote host address")
    parser.add_argument('--port', '-P', default=PORT, help="port")
    parser.add_argument('--user', '-u', default=USER, help="username")
    parser.add_argument('--password', '-p', default=PASS, help="password")
    args = parser.parse_args()

    xml = read_file(args.topology)
    reply = edit_config(xml, args.host, args.port, args.user, args.password)
    print('Command sent: {}'.format(reply.ok))


if __name__ == '__main__':
    sys.exit(main())
