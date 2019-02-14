import logging
from os import sys, path

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

logging.basicConfig(level=logging.DEBUG)

from lib.wss.wss import Wss

if __name__ == '__main__':
    wss_tx = "wss_tx"
    wss_tx_configfile = "SN042561.wsconfig"
    Wss.configuration(wss_tx, wss_tx_configfile, 1550.12, 0.0, 0.0, 25)
