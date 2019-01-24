import time
from os import sys, path

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from lib.laser.laser import Laser

IP_LASER = '10.1.1.7'

LASER_ADDR = '11'

if __name__ == '__main__':
    yenista = Laser(IP_LASER, LASER_ADDR)
    yenista.wavelength(3, 1550.12)
    yenista.power(3, 14.5)
    yenista.enable(3, True)
    time.sleep(5)
    print(yenista.status(3))
    print(yenista.test())
    yenista.close()

