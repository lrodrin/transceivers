import time
from os import sys, path

SECS = 5

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from lib.wss.wss import Wss


def wss_startup(name, config_filename, att, phase, bw, lambda0):
    wstx = Wss(name, config_filename)
    wstx.open()
    wstx.attenuation[0] = att
    wstx.phase[0] = phase
    wstx.bandwidth[0] = bw
    wstx.wavelength[0] = lambda0
    wstx.execute()
    time.sleep(SECS)
    result = wstx.check_profile()
    print('BW = ', result[0])
    # print('BW = {}, ATT = {}'.format(result[0], result[1]))
    wstx.close()


if __name__ == '__main__':
    wstx_name = "wstx"
    wstx_config_filename = "SN042561.wsconfig"
    wss_startup(wstx_name, wstx_config_filename, 0.0, 0.0, 25, 1550.12)
