import logging
import time
from os import sys, path

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

logging.basicConfig(level=logging.DEBUG)

from lib.laser.laser import Laser

if __name__ == '__main__':
    ip = '10.1.1.7'
    channel_tls1 = 2
    channel_tls2 = 3
    addr = '11'
    lambda0 = 1550.12
    power_tls1 = 14.5
    power_tls2 = 14.5
    start_time = time.time()
    # Laser.configuration(ip, addr, channel_tls1, lambda0, power_tls1)
    # Laser.configuration(ip, addr, channel_tls2, lambda0, power_tls2)
    print("--- %s seconds ---" % (time.time() - start_time))
