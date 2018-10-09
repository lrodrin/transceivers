#!/usr/bin/env python

import argparse
import sys

import requests

from restconf.defaults import *
from restconf.helpers import *

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"


def post(json, host, port, user, pwd):
    url = 'http://' + host + ':' + str(port) + '/v1.0/topology/switches'
    response = requests.post(url, json, auth=(user, pwd))
    print(response.json)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--topology', '-t', default=JSON, help="JSON Topology configuration file")
    parser.add_argument('--host', '-H', default=HOST, help="remote host address")
    parser.add_argument('--port', '-P', default=PORT, help="port")
    parser.add_argument('--user', '-u', default=USER, help="username")
    parser.add_argument('--password', '-p', default=PASS, help="password")
    args = parser.parse_args()

    json = read_file(args.topology)
    reply = post(json, args.host, args.port, args.user, args.password)
    print('Command sent: {}'.format(reply.ok))


if __name__ == '__main__':
    sys.exit(main())
