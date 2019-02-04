import logging
import time
from logging.handlers import RotatingFileHandler

import requests
from flask import Flask, request, json, Response
from os import sys, path

SPEED_OF_LIGHT = 299792458

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from lib.laser.laser import Laser
from lib.amp.amp import Amplifier

URL = 'http://10.1.1.10:5000/api/'
HEADERS = {"Content-Type": "application/json"}

app = Flask(__name__)


@app.route('/api/hello', methods=['GET'])
def hello_world():  # TODO esborrar quan fucnioni tot
    log.info('This is a info message!')
    log.debug('This is a debug message!')
    log.error('This is a error message!')
    log.warning('This is a warning message!')
    return Response(response=json.dumps('Hello, World!'), status=200, mimetype='application/json')


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
        log.debug("Laser - status: {}, wavelength: {}, power: {}".format(result[0], result[1], result[2]))
        # print(yenista.test())
        yenista.close()
    except Exception as e:
        log.debug("ERROR {}".format(e))


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
        time.sleep(5)
        manlight.enable(status)
        result = manlight.status()
        log.debug("Amplifier - status: {}, mode: {}, power: {}".format(result[0], result[1], result[2]))
        # print(manlight.test())
        manlight.close()
    except Exception as e:
        log.debug("ERROR {}".format(e))


def python_xc(cl, och):
    """
    Show the client assigned to the optical channel.

    :param cl: client
    :type cl: int
    :param och: optical channel assigned
    :type och: int
    """
    return log.debug("Client %s assigned to optical channel %s" % (cl, och))


def python_f(och, freq, power, mode):
    """
    Terminal Optical Channel Configuration.
        - Laser configuration
        - Amplifiers configuration.
        - DAC configuration.
        - OSC configuration.

    :param och: optical channel id
    :type och: int
    :param freq: frequency of the laser
    :type freq: float
    :param power: power of the Laser
    :type power: float
    :param mode: operational mode for the optical channel
    :type mode: int
    """
    # Laser configuration
    lambda0 = (SPEED_OF_LIGHT / (freq * 1e6)) * 1e9  # Wavelength in nm
    power = power + 9  # comptant les perdues per culpa de la modulacio optica # TODO cas modulacio optica ?
    # channel 1 - 193.4e6 = 1550.119
    # channel 2 - 193.3e6 = 1550.918
    if freq == 193.4e6:
        laser_startup('10.1.1.7', '11', 1, lambda0, power, True)
    elif freq == 193.3e6:
        laser_startup('10.1.1.7', '11', 2, lambda0, power, True)

    # Amplifiers configuration
    # TODO passar params
    amplifier_startup('10.1.1.16', '3', "APC", 3.20, True)  # 3.20 uniform loading
    amplifier_startup('10.1.1.15', '3', "APC", 0.4, True)   # 0.4 ?

    # DAC configuration
    # TODO passar params
    params_dac = {'trx_mode': 0, 'tx_ID': 1, 'FEC': 'SD-FEC', 'bps': 2, 'pps': 0}
    request_dac = requests.post(URL + 'dac', headers=HEADERS, data=json.dumps(params_dac))
    print(request_dac.content)

    # OSC configuration
    # TODO passar params
    params_osc = {'trx_mode': 0, 'rx_ID': 1, 'FEC': 'SD-FEC', 'bps': 2, 'pps': 0}
    request_dac = requests.post(URL + 'osc', headers=HEADERS, data=json.dumps(params_osc))
    print(request_dac.content)


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
        s = python_xc(payload['client'], payload['och'])
        return s

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
    payload = request.json  # Och, freq, power, mode values from agent
    try:
        python_f(payload['och'], payload['freq'], payload['power'], payload['mode'])
        return log.debug("Optical Channel was successfully configured\n")

    except OSError as error:
        return log.debug("ERROR: {} \n".format(error))


if __name__ == '__main__':
    # File Handler
    fileHandler = RotatingFileHandler('server.log', maxBytes=10000000, backupCount=5)
    # Stream Handler
    streamHandler = logging.StreamHandler()
    # Create a Formatter for formatting the log messages
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(filename)s: %(message)s")
    # TODO Add formatter
    # Add the Formatter to the Handler
    # fileHandler.setFormatter(formatter)
    # streamHandler.setFormatter(formatter)
    # Create the Logger
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.DEBUG)
    # Add Handlers to the Logger
    log.addHandler(fileHandler)
    log.addHandler(streamHandler)
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=False)
