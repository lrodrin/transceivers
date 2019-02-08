import array

import numpy as np
import requests
import json
import time
import logging

from os import sys, path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
logging.basicConfig(filename='agent.logs',level=logging.DEBUG)  # TODO fitxer de logs comu

from lib.laser.laser import Laser
from lib.amp.amp import Amplifier
from lib.wss.wss import Wss
from lib.dac.dac import DAC
from lib.osc.osc import OSC


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
    log.debug("Laser startup")
    try:
        yenista = Laser(ip, addr)
        yenista.wavelength(ch, lambda0)
        yenista.power(ch, power)
        yenista.enable(ch, status)
        time.sleep(5)
        result = yenista.status(ch)
        log.debug("Laser - status: {}, wavelength: {}, power: {}".format(result[0], result[1], result[2]))
        yenista.close()
    except Exception as e:
        log.debug("ERROR {}".format(e))



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
# int and float arrays of 512 positions examples cas uniform

url = 'http://0.0.0.0:5000/api/'
headers = {"Content-Type": "application/json"}

request = requests.get(url + 'hello', headers=headers)
print(request.content)

# DAC configuration
params = {'tx_ID': 0, 'trx_mode': 0, 'FEC': 'SD-FEC', 'bn': bn, 'En': En}
request = requests.post(url + 'blue/dac', headers=headers, data=json.dumps(params))
print(request.content)

# OSC configuration
params = {'rx_ID': 0, 'trx_mode': 0, 'FEC': 'SD-FEC', 'bn': bn, 'En': En}
request = requests.post(url + 'blue/osc', headers=headers, data=json.dumps(params))
print(request.content)
