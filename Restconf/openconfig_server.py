import logging
from logging.handlers import RotatingFileHandler
from os import sys, path

import requests
from flask import Flask, request, json, jsonify

ADDR_AMPLIFIER = '3'
IP_AMPLIFIER_2 = '10.1.1.15'
IP_AMPLIFIER_1 = '10.1.1.16'
ADDR_LASER = '11'
IP_LASER = '10.1.1.7'
SPEED_OF_LIGHT = 299792458
URL_DAC_OSC_SERVER = 'http://10.1.7.64:5000/api/'
HEADERS = {"Content-Type": "application/json"}

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from lib.laser.laser import Laser
from lib.amp.amp import Amplifier

app = Flask(__name__)


@app.route('/api/vi/openconfig/hello', methods=['GET'])
def hello_world():  # TODO delete
    if request.method == 'GET':
        try:
            logger.info('This is a info message!')
            logger.debug('This is a debug message!')
            logger.error('This is a error message!')
            logger.warning('This is a warning message!')
            return jsonify('Hello, World!', 200)

        except Exception as e:
            logger.error(e)
            raise e


@app.route('/api/vi/openconfig/local_assignment', methods=['POST'])
def local_assignment():
    """
    # TODO

    post: # TODO
        summary: # TODO
        description: Reference to the line-side optical channel that should carry the current logical channel element.
        Use this reference to exit the logical element stage.
        attributes:
            - name: client
              description: Identify the client to be used.
              type: string (0 for C1 or 1 for C2)
            - name: och
              description: Identify the optical channel to be used.
              type: string

        responses:
            200:
                description: (str) Client was successfully assigned to optical channel.
            500:
                description: (str) Error message in case there is some error.
    """
    if request.method == 'POST':
        params = request.json
        if params is not None:
            cl = params['client']
            och = params['och']
            try:
                msg = "Client {} assigned to the optical channel {}".format(cl, och)
                logger.debug(msg)
                return jsonify(msg, 200)

            except Exception as e:
                logger.error(e)
                return jsonify(e, 500)
        else:
            raise ValueError('The parameters sended by the agent are not correct.')


@app.route('/api/vi/openconfig/optical_channel', methods=['POST'])
def optical_channel_configuration():
    """
    Optical Channel Configuration route.

    post:
        summary: Configuration of the terminal optical channel (och).
        description: Configure the optical channel och by setting frequency, power and mode.
        attributes:
            - name: och
              description: Optical channel.
              type: str
            - name: freq
              description: Frequency of the Laser, expressed in MHz.
              type: int
            - name: pow
              description: Power of the Laser, expressed in increments of 0.01 dBm.
              type: int
            - name: mode
              description: Vendor-specific mode identifier -- sets the operational mode for the channel. The specified
              operational mode must exist in the list of supported operational modes supplied by the device.
              type: int

        responses:
            200:
                description: (string) Optical Channel was successfully configured.
           500:
                description: (str) Error message in case there is some error.

    """
    if request.method == 'POST':
        params = request.json
        och = params['och']
        freq = params['freq']
        power = params['power']
        mode = params['mode']
        if params is not None:
            try:
                logger.debug("Optical Channel configuration started")
                python_f(och, freq, power, mode)
                return jsonify("Optical Channel was successfully configured", 200)

            except Exception as e:
                logger.error(e)
                return jsonify(e, 500)
        else:
            raise ValueError('The parameters sended by the agent are not correct.')


def python_f(och, freq, power, mode):
    """
    Terminal Optical Channel Configuration:

        - Laser configuration.
            - channel 1 = freq 193.4e6 = lambda0 1550.119
            - channel 2 = freq 193.3e6 = lambda0 1550.918
        - Amplifiers configuration.
            - mode: APC, AGC or ACC.
            - power: 3.20 uniform loading or 0.4 loading
        - DAC configuration.
        - OSC configuration.

    :param och: Laser channel id
    :type och: int
    :param freq: frequency of the laser
    :type freq: float
    :param power: power of the Laser
    :type power: float
    :param mode: operational mode for the optical channel
    :type mode: int
    """
    vars = init_variables()
    logger.debug("Laser configuration started")
    lambda0 = (SPEED_OF_LIGHT / (freq * 1e6)) * 1e9  # wavelength in nm
    power = power + 9  # counting the losses because of optical modulation
    # TODO
    # if power == x:
    # elif power == y:
    Laser.configuration(IP_LASER, ADDR_LASER, och, lambda0, power, vars['laser'])
    logger.debug("Laser configuration finished")

    logger.debug("Amplifiers configuration started")
    Amplifier.configuration(IP_AMPLIFIER_1, ADDR_AMPLIFIER, vars['amplifier'][0], vars['amplifier'][1],
                            vars['amplifier'][2])
    Amplifier.configuration(IP_AMPLIFIER_2, ADDR_AMPLIFIER, vars['amplifier'][0], vars['amplifier'][1],
                            vars['amplifier'][2])
    logger.debug("Amplifiers configuration finished")

    logger.debug("DAC configuration started")
    request = requests.post(URL_DAC_OSC_SERVER + 'dac_osc_configuration', headers=HEADERS,
                            data=json.dumps(vars['dac_osc']))
    if request:
        data = request.json()
        logger.debug(data)
        logger.debug("DAC and OSC configuration finished")
    else:
        logger.error("DAC and OSC configuration not finished")


def init_variables():
    """
    # TODO
    :return:
    :rtype: dict
    """
    params_dac_osc = {'conf_mode': 0, 'trx_mode': 1, 'tx_ID': 0, 'rx_ID': 0, 'bn': 2, 'En': 0, 'eq': 0}
    d = {
        'laser': True,
        'amplifier': ["APC", 7.5, True],
        'dac_osc': params_dac_osc
    }
    return d


if __name__ == '__main__':
    # File Handler
    # fileHandler = RotatingFileHandler('metro-haul/server.log', maxBytes=10000000, backupCount=5)
    fileHandler = RotatingFileHandler('server.log', maxBytes=10000000, backupCount=5)
    # Stream Handler
    streamHandler = logging.StreamHandler()
    # Create a Formatter for formatting the logs messages
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(filename)s: %(message)s")
    # TODO Add formatter
    # Add the Formatter to the Handler
    # fileHandler.setFormatter(formatter)
    # streamHandler.setFormatter(formatter)
    # Create the Logger
    logger = logging.getLogger('werkzeug')
    logger.setLevel(logging.DEBUG)
    # Add Handlers to the Logger
    logger.addHandler(fileHandler)
    logger.addHandler(streamHandler)
    app.run(host='0.0.0.0', port=5001, debug=True, threaded=False)
