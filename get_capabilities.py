#!/usr/bin/env python

import argparse
import re
import sys

from defaults import *
from ncclient import manager

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"


def get_capabilities(host, port, user, pwd):
    with manager.connect(host=host, port=port, username=user, password=pwd,
                         hostkey_verify=False, device_params={'name': 'default'}) as m:
        capabilities = m.server_capabilities

    return capabilities


def print_capabilities(c, pattern):
    print(
        "Search pattern:" + pattern)
    filtered_c = [x for x in c if re.search(pattern, x, re.IGNORECASE)]
    for one in filtered_c:
        print(one)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--search', '-s', default='', help="Filter for list of capabilities")
    parser.add_argument('--host', '-H', default=HOST, help="remote host address")
    parser.add_argument('--port', '-P', default=PORT, help="port")
    parser.add_argument('--user', '-u', default=USER, help="username")
    parser.add_argument('--password', '-p', default=PASS, help="password")
    args = parser.parse_args()

    result = get_capabilities(args.host, args.port, args.user, args.password)

    print_capabilities(result, args.search)


if __name__ == '__main__':
    sys.exit(main())
