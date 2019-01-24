import time
from os import sys, path

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from lib.laser.laser import Laser

IP_LASER = '10.1.1.7'
SECS = 5
LASER_ADDR = '11'


def laser_startup(och, lamba0, pow, stat):
    yenista = Laser(IP_LASER, LASER_ADDR)
    yenista.wavelength(och, lamba0)
    yenista.power(och, pow)
    yenista.enable(och, stat)
    time.sleep(SECS)
    print(yenista.status(och))
    print(yenista.test())
    yenista.close()


if __name__ == '__main__':
    laser_startup(3, 1560.12, 7.5, True)
