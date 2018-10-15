import argparse
import logging
import sys
import time

from netconf import nsmap_add
from netconf import server

nsmap_add("sys", "urn:ietf:params:xml:ns:yang:ietf-system")


class SystemServer(object):
    def __init__(self, port, auth, debug):
        self.server = server.NetconfSSHServer(auth, self, port, debug)

    def close(self):
        self.server.close()


def main(*margs):

    parser = argparse.ArgumentParser("Example Netconf Server")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--password", default="admin", help='Netconf password')
    parser.add_argument('--port', type=int, default=8300, help='Netconf server port')
    parser.add_argument("--username", default="admin", help='Netconf username')
    args = parser.parse_args(*margs)

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    auth = server.SSHUserPassController(username=args.username, password=args.password)
    s = SystemServer(args.port, auth, args.debug)

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
