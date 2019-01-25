import time

import requests
from flask import Flask, request, json
from os import sys, path

TIME_SLEEP = 5
AMPLIFIER_ADDR = '3'
IP_AMPLIFIER_2 = '10.1.1.16'
IP_AMPLIFIER_1 = '10.1.1.15'
IP_LASER = '10.1.1.7'
LASER_ADDR = '11'
SPEED_OF_LIGHT = 299792458
URL = 'http://10.1.1.10:5000/api/'
HEADERS = {"Content-Type": "application/json"}

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from lib.laser.laser import Laser
from lib.amp.amp import Amplifier

app = Flask(__name__)


@app.route('/api/hello', methods=['GET'])
def hello_world():  # TODO esborrar quan fucnioni tot
    return 'Hello, World!'


def python_xc(cl, och):
    """
    Show the client assigned to the optical channel.

    :param cl: client
    :param och: optical channel assigned
    :type cl: str
    :type och: str
    """
    return "Client " + cl + " assigned to optical channel " + och


@app.route('/api/vi/openconfig/local_assignment', methods=['POST'])
def local_assignment():
    """
    ? route.

    post:
    summary: ?.
    description: Reference to the line-side optical channel that should carry the current logical
    channel element. Use this reference to exit the logical element stage.
    attributes:
        - name: client
          description: Identify the client to be used.
          type: string (C1 or C2)
        - name: Och
          description: Identify the optical channel to be used.
          type: string

        responses:
            200:
                description: (string) Client was successfully assigned to optical channel.
            404:
                description: (string) Error message in case there is some error.

    """
    payload = request.json  # client, Och from agent
    try:
        python_xc(payload['client'], payload['Och'])

    except OSError as error:
        return "ERROR: {} \n".format(error)


def python_f(och, freq, powL, statL, modeA, modeB, powA, powB, statA, statB, params_dac, params_osc):
    """
    Terminal Optical Channel Configuration.
        - Laser configuration
        - Amplifiers configuration.
        - Waveshaper configuration.
        - DAC configuration.
        - OSC configuration.

    :param och: optical channel
    :param freq: frequency of the laser
    :param powL: power of the laser
    :param statL: status of the laser
    :param modeA: mode of the amplifiers A
    :param modeB: mode of the amplifiers B
    :param powA: power of amplifier A
    :param powB: power of amplifier B
    :param statA: status of the amplifier A
    :param statB: status of the amplifier B
    :param params_dac: {'tx_ID': 0, 'trx_mode': 0, 'FEC': 'SD-FEC', 'bps': bps, 'pps': pps}
    :param params_osc: {'rx_ID': 0, 'trx_mode': 0, 'FEC': 'SD-FEC', 'bps': bps, 'pps': pps}
    :type och: int
    :type freq: str
    :type powL: float
    :type statL: bool
    :type modeA: str
    :type modeB: str
    :type powA: float
    :type powB: float
    :type statA: bool
    :type statB: bool
    """
    # Laser configuration
    lambda0 = (SPEED_OF_LIGHT / (freq * 1e6)) * 1e9  # Wavelength in nm
    print(laser_startup(och, lambda0, powL, statL))
    # Amplifiers configuration
    print(amplifier_startup(IP_AMPLIFIER_1, AMPLIFIER_ADDR, modeA, powA, statA))
    print(amplifier_startup(IP_AMPLIFIER_2, AMPLIFIER_ADDR, modeB, powB, statB))
    # DAC configuration
    request_dac = requests.post(URL + 'dac', headers=HEADERS, data=json.dumps(params_dac))
    print(request_dac.content)
    # OSC configuration
    request_dac = requests.post(URL + 'dac', headers=HEADERS, data=json.dumps(params_osc))
    print(request_dac.content)


def laser_startup(och, lambda0, pow, stat):
    """
    Laser Configuration.

    :param och: optical channel
    :param lambda0: wavelength
    :param pow: power
    :param stat: enable/disable status
    :type och: int
    :type lambda0: int
    :type pow: float
    :type stat: bool
    :return: laser configured or not
    :rtype: str
    """
    try:
        yenista = Laser(IP_LASER, LASER_ADDR)
        yenista.wavelength(och, lambda0)
        yenista.power(och, pow)
        yenista.enable(och, stat)
        time.sleep(TIME_SLEEP)
        print(yenista.status(och))
        print(yenista.test())
        yenista.close()
        return "Laser {} was successfully configured\n".format(IP_LASER)

    except OSError as error:
        return "ERROR: {} \n".format(error)


def amplifier_startup(ip, addr, mode, pow, stat):
    """
    Amplifier configuration.

    :param ip: ip address
    :param addr: addr address
    :param mode: mode
    :param pow: power
    :param stat: enable/disable status
    :return: amplifier configured or not
    :rtype: str
    """
    try:
        manligh = Amplifier(ip, addr)
        manligh.mode(mode, pow)
        manligh.enable(stat)
        time.sleep(5)
        print(manligh.status())
        print(manligh.test())
        manligh.close()
        return "Amplifier {} was successfully configured\n".format(ip)

    except OSError as error:
        return "ERROR: {} \n".format(error)


@app.route('/api/vi/openconfig/optical_channel', methods=['POST'])
def optical_channel_configuration():
    """
    Optical Channel Configuration route.

    post:
        summary: Configuration of the terminal optical channel (Och).
        description: Configure the optical channel Och by setting frequency, power and mode of the optical channel.
        attributes:
            - name: Och
              description: Optical channel.
              type: string
            - name: freq
              description: Frequency of the optical channel, expressed in MHz.
              type: int
            - name: pow
              description: Power of the optical channel, expressed in increments of 0.01 dBm.
              type: int
            - name: mode
              description: Vendor-specific mode identifier -- sets the operational mode for the channel. The specified
              operational mode must exist in the list of supported operational modes supplied by the device.
              type: int

        responses:
            200:
                description: (string) Optical Channel was successfully configured.
            404:
                description: (string) Error message in case there is some error.

    """
    payload = request.json  # Och, freq, powL, statL, modeA, modeB, powA, powB, statA, statB from agent
    # params_dac = {'tx_ID': 0, 'trx_mode': 0, 'FEC': 'SD-FEC', 'bps': bps, 'pps': pps}
    # params_osc = {'rx_ID': 0, 'trx_mode': 0, 'FEC': 'SD-FEC', 'bps': bps, 'pps': pps}
    try:
        python_f(payload['Och'], payload['freq'], payload['powL'], payload['statL'], payload['modeA'], payload['modeB'],
                 payload['powA'], payload['powB'], payload['statA'], payload['statB'], payload['params_dac'],
                 payload['params_osc'])
        return "Optical Channel was successfully configured\n"

    except OSError as error:
        return "ERROR: {} \n".format(error)


if __name__ == '__main__':
    # app.run(host='10.1.7.65', port=5000, debug=True)  # REAL
    app.run(host='127.0.0.1', port=5000, debug=True)  # TEST
