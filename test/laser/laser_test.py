import time
from os import sys, path

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from lib.laser.laser import Laser


def laser_startup(ip, addr, ch, lambda0, power, status):
    """
    Laser startup.

    :param ip: IP address of GPIB-ETHERNET
    :type ip: str
    :param addr: GPIB address
    :type addr: str
    :param ch: channel
    :type ch: int
    :param lambda0: wavelength
    :type lambda0: float
    :param power: power
    :type power: float
    :param status: if True is enable otherwise is disable
    :type status: bool
    """
    print("Laser startup")
    try:
        yenista = Laser(ip, addr)
        yenista.wavelength(ch, lambda0)
        yenista.power(ch, power)
        yenista.enable(ch, status)
        time.sleep(5)
        result = yenista.status(ch)
        print("Laser - status: {}, wavelength: {}, power: {}".format(result[0], result[1], result[2]))
        # print(yenista.test())
        yenista.close()
    except Exception as e:
        print("ERROR {}".format(e))


if __name__ == '__main__':
    ip = '10.1.1.7'
    addr = '11'
    laser_startup(ip, addr, 3, 1560.12, 7.5, True)
