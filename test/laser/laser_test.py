import time

from lib.laser.laser import *

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"


if __name__ == '__main__':
    ip_eth = '10.1.1.7'
    addr_gpib = '11'
    yenista = Laser(ip_eth, addr_gpib)
    yenista.wavelength(3, 1550.11)
    yenista.power(3, 13.5)
    yenista.enable(3, True)
    time.sleep(5)
    print(yenista.status(3))
    print(yenista.test())
    yenista.close()
