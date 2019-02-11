import logging
from os import sys, path

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

logging.basicConfig(level=logging.DEBUG)

from lib.amp.amp import Amplifier

if __name__ == '__main__':
    ip_1 = '10.1.1.16'
    ip_2 = '10.1.1.15'
    addr = '3'
    mode = "APC"
    power = 7.5
    Amplifier.configuration(ip_1, addr, mode, power, True)
    Amplifier.configuration(ip_2, addr, mode, power, True)
