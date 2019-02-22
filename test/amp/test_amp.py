import logging
from os import sys, path

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

logging.basicConfig(level=logging.DEBUG)

from lib.amp.amp import Amplifier

if __name__ == '__main__':
    ip = '10.1.1.16'
    addr = '3'
    mode = "APC"
    power = 0
    status = True
    Amplifier.configuration(ip, addr, mode, power, status)
