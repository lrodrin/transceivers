import time

from os import sys, path

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from lib.amp.amp import Amplifier


def amplifier_startup(ip, addr, mode, power, status):
    """
    Amplifier startup.

    :param ip: IP address of GPIB-ETHERNET
    :type ip: str
    :param addr: GPIB address
    :type addr: str
    :param mode: mode
    :type mode:str
    :param power: power
    :type power: float
    :param status: if True is enable otherwise is disable
    :type status: bool
    """
    print("Amplifier startup")
    try:
        manlight = Amplifier(ip, addr)
        manlight.mode(mode, power)
        time.sleep(1)
        manlight.enable(status)
        result = manlight.status()
        print("Amplifier - status: {}, mode: {}, power: {}".format(result[0], result[1], result[2]))
        # print(manlight.test())
        manlight.close()
    except Exception as e:
        print("ERROR {}".format(e))


if __name__ == '__main__':
    ip = '10.1.1.16'
    addr = '3'
    amplifier_startup(ip, addr, "APC", 7.5, True)
