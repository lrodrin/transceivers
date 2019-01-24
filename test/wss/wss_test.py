import time
from os import sys, path

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from lib.wss.wss import Wss

if __name__ == '__main__':
    wstx_name = "wstx"
    wstx_config_filename = "SN042561.wsconfig"  # TODO link to file
    wstx = Wss(wstx_name, wstx_config_filename)
    wstx.open()
    wstx.attenuation[0] = 0.0
    wstx.phase[0] = 0.0
    wstx.bandwidth[0] = 25
    wstx.wavelength[0] = 1550.12  # nm
    wstx.execute()
    time.sleep(5)
    [BW_wss, read_att] = wstx.check_profile()
    print('Bw', BW_wss)
    wstx.close()
