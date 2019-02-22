import logging
from os import sys, path

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

logging.basicConfig(level=logging.DEBUG)

from lib.laser.laser import Laser

if __name__ == '__main__':
    ip = '10.1.1.7'
    channel = 1
    # channel 1 - lambda0 1550.12
    # channel 2 - lambda0 1550.9
    addr = '11'
    lambda0 = 1550.12
    power = 7.5
    status = True
    Laser.configuration(ip, addr, channel, lambda0, power, status)
