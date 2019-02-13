import logging
import requests
from logging.handlers import RotatingFileHandler
from os import sys, path

from flask import Flask, request, json, jsonify
from flasgger import Swagger

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from lib.laser.laser import Laser
from lib.amp.amp import Amplifier

IP_LASER = '10.1.1.7'
IP_AMPLIFIER_1 = '10.1.1.16'
IP_AMPLIFIER_2 = '10.1.1.15'
ADDR_LASER = '11'
ADDR_AMPLIFIER = '3'
SPEED_OF_LIGHT = 299792458
URL_DAC_OSC_SERVER = 'http://10.1.7.64:5000/api/'
HEADERS = {"Content-Type": "application/json"}

app = Flask(__name__)
Swagger(app)


@app.route('/api/vi/openconfig/hello', methods=['GET'])
def hello_world():  # TODO delete route
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
    Function that assigns a client Cx to a optical channel Ochx 
    ---
    post:
    description: |
        Reference to the line-side optical channel that should carry the current logical channel element. Use this
        reference to exit the logical element stage
    parameters:
    - name: client
      in: body
      type: integer
      description: Identify the client to be used
      example: 0 for C1 or 1 for C2
    - name: och
      in: body
      type: integer
      description: Identify the optical channel to be used
    responses:
        200:
            description: "Successful operation"
        405:
            description: "Invalid input"
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
    Optical Channel Configuration
    ---
    post:
    description: Configuration of the optical channel by setting frequency, optical power and operational mode
    parameters:
    - name: och
      in: body
      type: integer
      description: Optical channel id.
      example: 1 or 2
    - name: freq
      in: body
      type: integer
      description: |
        Frequency of the optical channel expressed in MHz. 
      example: 193.3e6 or 193.4e6
    - name: power
      in: body
      type: float
      description: Target optical power of level of the optical channel expressed in increments of 0.01 dBm
      example: 3.20 uniform loading or 0.4 loading
    - name: mode
      in: body
      type: integer
      description: |
            Vendor-specific mode identifier. Sets the operational mode for the channel. The specified operational mode
            must exist in the list of supported operational modes supplied by the device. Example: FEC mode (SD, HD, %OH)
    responses:
        200:
            description: "Successful operation"
        405:
            description: "Invalid input"
    """
    if request.method == 'POST':
        params = request.json
        if params is not None:
            och = params['och']
            freq = params['freq']
            power = params['power']
            mode = params['mode']
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
    Run Optical Channel Configuration:

        - Run Laser configuration.
        - Run Amplifiers configuration.
        - Run DAC configuration.
        - Run OSC configuration.

    :param och: Laser channel id. 1 for channel 1 and 2 for channel 2
    :type och: int
    :param freq: Frequency of the optical channel expressed in MHz.  e.g. 193.4e6 (1550.119) for channel 1 and 193.3e6
    (1550.918) for channel 2
    :type freq: int
    :param power: Target optical power of level of the optical channel expressed in increments of 0.01 dBm.
    (e.g. 3.20 uniform loading or 0.4 loading)
    :type power: float
    :param mode: Operational mode for the optical channel
    :type mode: int
    """
    params = init_variables()
    logger.debug("Laser configuration started")
    lambda0 = (SPEED_OF_LIGHT / (freq * 1e6)) * 1e9  # wavelength in nm
    if params['dac_osc']['conf_mode'] == 0:
        power += 9  # To take into account the losses of the modulation (MZM)

    Laser.configuration(IP_LASER, ADDR_LASER, och, lambda0, power, params['laser_status'])
    logger.debug("Laser configuration finished")

    logger.debug("Amplifiers configuration started")
    Amplifier.configuration(IP_AMPLIFIER_1, ADDR_AMPLIFIER, params['amplifier'][0], params['amplifier'][1],
                            params['amplifier'][2])
    Amplifier.configuration(IP_AMPLIFIER_2, ADDR_AMPLIFIER, params['amplifier'][0], params['amplifier'][1],
                            params['amplifier'][2])
    logger.debug("Amplifiers configuration finished")

    logger.debug("DAC and OSC configuration started")
    response = requests.post(URL_DAC_OSC_SERVER + 'dac_osc_configuration', headers=HEADERS,
                             data=json.dumps(params['dac_osc']))
    if response:
        data = response.json()
        logger.debug(data)
        logger.debug("DAC and OSC configuration finished")
    else:
        logger.error("DAC and OSC configuration not finished")


def init_variables():
    """
    Initialization of the necessary variables for the configuration of an optical channel:

        - Laser variables contains enable or disable status.
        - Amplifiers variables contains mode, power and enable or disable status.
        - DAC and OSC variables contains configuration mode, transceiver mode, transceiver id, receiver id,
        bits per symbol per subcarrier, power per subcarrier figure and equalization.

    :return: a dictionary with the variables of Laser, Amplifiers, DAC and OSC
    :rtype: dict
    """
    d = {
        'laser_status': True,
        'amplifier': ["APC", 7.5, True],
        'dac_osc': {'conf_mode': 0, 'trx_mode': 1, 'tx_ID': 0, 'rx_ID': 0, 'bn': 2, 'En': 0, 'eq': 0}
    }
    return d


if __name__ == '__main__':
    # File Handler
    # fileHandler = RotatingFileHandler('server/server.log', maxBytes=10000000, backupCount=5)
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
