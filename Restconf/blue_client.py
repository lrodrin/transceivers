import requests
# import json
import time

from os import sys, path

SECS = 5
AMPLIFIER_ADDR = '3'
IP_AMPLIFIER_2 = '10.1.1.16'
IP_AMPLIFIER_1 = '10.1.1.15'
IP_LASER = '10.1.1.7'
LASER_ADDR = '11'

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from lib.laser.laser import Laser
from lib.amp.amp import Amplifier
from lib.wss.wss import Wss


def laser_startup(och, lamba0, pow, stat):
    yenista = Laser(IP_LASER, LASER_ADDR)
    yenista.wavelength(och, lamba0)
    yenista.power(och, pow)
    yenista.enable(och, stat)
    time.sleep(SECS)
    print(yenista.status(och))
    print(yenista.test())
    yenista.close()


def amplifier_startup(modeA, powA, modeB, powB, statA, statB):
    manlight_1 = Amplifier(IP_AMPLIFIER_1, AMPLIFIER_ADDR)
    manlight_2 = Amplifier(IP_AMPLIFIER_2, AMPLIFIER_ADDR)
    manlight_1.mode(modeA, powA)
    manlight_2.mode(modeB, powB)
    manlight_1.enable(statA)
    manlight_2.enable(statB)
    time.sleep(5)
    print(manlight_1.status())
    print(manlight_2.status())
    print(manlight_1.test())
    print(manlight_2.test())
    manlight_1.close()
    manlight_2.close()


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


# Laser configuration
# laser_startup(3, 1560.12, 7.5, True)

# Amplifiers configuration
# amplifier_startup("APC", 5, "APC", 3, True, True)

# Waveshaper configuration
wstx_name = "wstx"
wstx_config_filename = "SN042561.wsconfig"
# wss_startup(wstx_name, wstx_config_filename, 0.0, 0.0, 25, 1550.12)

# int and float arrays of 512 positions examples
# bps = array.array('i', [0] * 512)
# pps = array.array('f', [0] * 512)
# print(bps)
# print(pps)
#
# bps = [0] * 512
# pps = [0.0] * 512
# print(bps)
# print(pps)

# url = 'http://10.1.1.10:5000/api/'  # REAL
url = 'http://127.0.0.1:5000/api/'  # TEST
headers = {"Content-Type": "application/json"}

request = requests.get(url + 'hello', headers=headers)
print(request.content)

# DAC configuration
# params = {'tx_ID': 0, 'trx_mode': 0, 'FEC': 'SD-FEC', 'bps': bps, 'pps': pps}
# request = requests.post(url + 'blue/dac', headers=headers, data=json.dumps(params))
# print(request.content)

# OSC configuration
# params = {'rx_ID': 0, 'trx_mode': 0, 'FEC': 'SD-FEC', 'bps': bps, 'pps': pps}
# request = requests.post(url + 'blue/osc', headers=headers, data=json.dumps(params))
# print(request.content)
