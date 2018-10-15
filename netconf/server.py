import argparse
import logging
import os
import sys
import time

from netconf import nsmap_add
from netconf import server

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

nsmap_add("sliceable-transceiver-sdm", "urn:sliceable-transceiver-sdm")


def parse_password_arg(password):
    if password:
        if password.startswith("env:"):
            unused, key = password.split(":", 1)
            password = os.environ[key]
        elif password.startswith("file:"):
            unused, path = password.split(":", 1)
            password = open(path).read().rstrip("\n")
    return password


class SystemServer(object):
    def __init__(self, port, host_key, auth, debug):
        self.server = server.NetconfSSHServer(auth, self, port, host_key, debug)

    def close(self):
        self.server.close()


def main(*margs):
    parser = argparse.ArgumentParser("Example Netconf Server")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--password", default="admin", help='Use "env:" or "file:" prefix to specify source')
    parser.add_argument('--port', type=int, default=830, help='Netconf server port')
    parser.add_argument("--username", default="admin", help='Netconf username')
    args = parser.parse_args(*margs)

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    args.password = parse_password_arg(args.password)
    host_key = os.path.dirname(__file__) + "/server-key"

    auth = server.SSHUserPassController(username=args.username, password=args.password)
    s = SystemServer(args.port, host_key, auth, args.debug)

    if sys.stdout.isatty():
        print("^C to quit server")
    try:
        while True:
            time.sleep(1)
    except Exception:
        print("quitting server")

    s.close()


if __name__ == "__main__":
    main()
