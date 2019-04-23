import argparse
import ast
import logging
from logging.handlers import RotatingFileHandler
from os import sys, path

import numpy as np
from flasgger import Swagger
from flask import Flask, request
from flask.json import jsonify
from flask_ini import FlaskIni

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from agent_core import AgentCore
from lib.dac.dac import DAC

app = Flask(__name__)
app.iniconfig = FlaskIni()
Swagger(app)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('werkzeug')
logger.setLevel(logging.DEBUG)

with app.app_context():
    parser = argparse.ArgumentParser("OPENCONFIG Server")
    parser.add_argument('-a', metavar="AGENT", help='BVT Agent Configuration file')
    args = parser.parse_args()
    app.iniconfig.read(args.a)
    ac = AgentCore(
        app.iniconfig.get('laser', 'ip'),
        app.iniconfig.get('laser', 'addr'),
        app.iniconfig.get('laser', 'channel'),
        app.iniconfig.get('laser', 'power'),
        app.iniconfig.get('oa', 'ip'),
        app.iniconfig.get('oa', 'addr'),
        app.iniconfig.get('oa', 'mode'),
        app.iniconfig.get('oa', 'power'),
        ast.literal_eval(app.iniconfig.get('dac_osc', 'logical_associations')),
        ast.literal_eval(app.iniconfig.get('wss', 'operations')),
        app.iniconfig.get('rest_api', 'ip')
    )
    logging.debug("AGENT CORE linked with configuration {}".format(args.a))


@app.route('/api/v1/openconfig/logical_channel_assignment', methods=['POST'])
def logical_channel_assignment():
    """
    Client assignation to an Optical Channel
    ---
    post:
    description: Creates a logical assignation between a Client and an Optical Channel.
    consumes:
    - application/json
    produces:
    - application/json
    parameters:
    - name: params
      in: body
      description: Client and the Optical Channel to be assigned
      example: {'name': 'c1', 'och': 'channel-101', 'status': 'enabled', 'type': 'client'}
      required: true
    responses:
        200:
            description: Successful assignation
        400:
            description: Invalid input logical assignation
    """
    if request.method == 'POST':
        params = request.json
        if len(params) != 0:
            name = params['name']
            och = params['och']
            status = params['status']
            type = params['type']
            try:
                msg = "Client {} assigned to the Optical Channel {}".format(name, och)
                logger.debug(msg)
                return jsonify(msg, 200)

            except Exception as e:
                logger.error(
                    "Logical channel assignation between Client {} and Optical Channel {} failed. Error: {}".format(
                        name, och, e))
                raise e
        else:
            return jsonify("The parameters sent are not correct", 400)


@app.route('/api/v1/openconfig/logical_channel_assignment/<client>', methods=['DELETE'])
def remove_logical_channel_assignment(client):
    """
    Client assignation to an Optical Channel
    ---
    delete:
    description: Remove logical assignation between Client specified by client and an Optical Channel.
    produces:
    - application/json
    parameters:
    - name: client
      in: path
      description: id to identify the Client assigned to an Optical Channel to be deleted
      required: true
    responses:
        200:
            description: Successful operation
        400:
            description: Invalid Client ID supplied
        404:
            description: Assignation not found
    """
    if request.method == 'DELETE':
        och = "channel-101"  # TODO delete
        try:
            msg = "Client {} assigned to the Optical Channel {} removed".format(client, och)
            logger.debug(msg)
            return jsonify(msg, 200)

        except Exception as e:
            msg = "Client c{} assigned to the Optical Channel {} not removed. Error: {}".format(client, och, e)
            logger.error(msg)
            return jsonify(msg, 404)


@app.route('/api/v1/openconfig/optical_channel', methods=['POST'])
def optical_channel():
    """
    Optical Channel configuration
    ---
    post:
    description: Creates a configuration of an Optical Channel by setting frequency, power and mode.
    consumes:
    - application/json
    produces:
    - application/json
    parameters:
    - name: params
      in: body
      description: parameters of the Optical Channel to be configured
      example: {'frequency': '192300000', 'mode': '111', 'name': 'channel-101', 'power': '10.0', 'status': 'enabled',
      'type': 'optical_channel'}
      required: true
    responses:
        200:
            description: Successful configuration
        400:
            description: Invalid input parameters for an optical channel
    """
    if request.method == 'POST':
        params = request.json
        if len(params) != 0:
            freq = float(params['frequency'])
            mode = params['mode']
            name = params['name']
            power = float(params['power'])
            status = params['status']
            type = params['type']
            try:
                result = configuration(name, freq, power, mode)
                logger.debug("Optical Channel {} configured with average BER = {}".format(name, result))
                return jsonify(msg, 200)

            except Exception as e:
                logger.error("Optical Channel {} configuration failed. Error: {}".format(name, e))
                raise e
        else:
            return jsonify("The parameters sent are not correct", 400)


@app.route('/api/v1/openconfig/optical_channel/<och>', methods=['DELETE'])
def remove_optical_channel(och):
    """
    Optical Channel configuration
    ---
    delete:
    description: Remove the configuration of an Optical Channel specified by och
    produces:
    - application/json
    parameters:
    - name: och
      in: path
      type: integer
      description: id that identify the Optical Channel configuration to be removed
      required: true
    responses:
        200:
            description: Successful operation
        400:
            description: Invalid Optical Channel ID supplied
        404:
            description: Optical Channel not found
    """
    if request.method == 'DELETE':
        try:
            msg = "Optical Channel och%s configuration removed" % och
            logger.debug(msg)
            return jsonify(msg, 200)

        except Exception as e:
            msg = "Optical Channel och{} configuration not removed. Error: {}".format(och, e)
            logger.error(msg)
            return jsonify(msg, 404)


def configuration(och, freq, power, mode):
    """
    Configuration of an Optical Channel by setting frequency, power and mode.

        - Amplifier setup.
        - Laser setup.
        - DAC/OSC setup.

    :param och: name to identify the Optical Channel
    :type och: str
    :param freq: frequency of the Optical Channel expressed in MHz. Possible values: from 191.494 THz (1565.544 nm)
    to 195.256 THz (1527.55899 nm)
    :type freq: float
    :param power: power of the Optical Channel expressed in dBm. Possible values: -3.04dBm to 5.5dBm
    :type power: float
    :param mode: operational mode of the Optical Channel.
    :type mode: str
    """
    try:
        # OA setup
        ac.amplifier_setup()

        # Laser and DAC/OSC setup
        ac.power_laser += power
        bn = np.array(np.ones(DAC.Ncarriers) * DAC.bps, dtype=int).tolist()
        En = np.array(np.ones(DAC.Ncarriers)).tolist()
        eq = "MMSE"

        result = ac.setup(freq, bn, En, eq)
        return result[1]

    except Exception as e:
        logger.error("Configuration of Optical Channel {} failed, Error: {}".format(och, e))
        raise e


def define_logger():
    """
    Create, formatter and add Handlers (RotatingFileHandler and StreamHandler) to the logger.
    """
    fileHandler = RotatingFileHandler('openconfig_adapter.log', maxBytes=10000000,
                                      backupCount=5)  # File Handler
    streamHandler = logging.StreamHandler()  # Stream Handler
    # Create a Formatter for formatting the logs messages
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(filename)s: %(message)s")
    # Add the Formatter to the Handlers
    fileHandler.setFormatter(formatter)
    streamHandler.setFormatter(formatter)
    # Add Handlers to the logger
    logger.addHandler(fileHandler)
    logger.addHandler(streamHandler)


if __name__ == '__main__':
    define_logger()
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=False)
