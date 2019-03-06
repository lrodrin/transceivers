import logging
from os import sys, path

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

logging.basicConfig(level=logging.DEBUG)

from lib.amp.amp import Amplifier

if __name__ == '__main__':
    ip_oa1 = '10.1.1.16'
    ip_oa2 = '10.1.1.15'
    addr = '3'
    mode_oa1 = "APC"
    mode_oa2 = "APC"
    power_oa1 = 0
    power_oa2 = 0
    oa1_conf = Amplifier.configuration(ip_oa1, addr, mode_oa1, power_oa1)
    oa2_conf = Amplifier.configuration(ip_oa2, addr, mode_oa2, power_oa2)
    print(oa1_conf)
    print(oa2_conf)
