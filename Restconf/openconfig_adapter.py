import argparse
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

logger = logging.getLogger('werkzeug')
logger.setLevel(logging.DEBUG)

with app.app_context():
    parser = argparse.ArgumentParser("OPENCONFIG Adapter Server")
    parser.add_argument('-a', metavar="AGENT CORE", help='BVT Agent Core Configuration file')
    args = parser.parse_args()
    app.iniconfig.read(args.a)
    agent = AgentCore(
        app.iniconfig.get('laser', 'ip'),
        app.iniconfig.get('laser', 'addr'),
        None,
        None,
        app.iniconfig.get('laser', 'LdB'),
        app.iniconfig.get('oa', 'ip'),
        app.iniconfig.get('oa', 'addr'),
        app.iniconfig.get('oa', 'mode'),
        app.iniconfig.get('oa', 'power'),
        None,
        None,
        app.iniconfig.get('rest_api', 'ip')
    )
    logging.debug("AGENT CORE created with configuration file {}".format(args.a))


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
    - name: body
      in: body
      description: Client and the Optical Channel to be assigned
      example: {'name': 'c1', 'och': 'channel-101', 'status': 'enabled', 'type': 'client'}
      required: true
    responses:
        200:
            description: Successful assignation
        400:
            description: Invalid parameters supplied
    """
    if request.method == 'POST':
        params = request.json
        if len(params) != 0:
            name = params['name']
            och = params['och']
            status = params['status']
            type = params['type']
            try:
                cl_id = int(name.split('c')[1])  # client id numerical part
                och_id = int(och.split('-')[1])  # optical channel id numerical part
                if name == "c1" and och_id == 101:
                    agent.channel_laser = 2
                    agent.logical_associations.append({'id': cl_id, 'dac_out': 1, 'osc_in': 1})
                else:
                    agent.channel_laser = 3
                    agent.logical_associations.append({'id': cl_id, 'dac_out': 2, 'osc_in': 2})

                msg = "Client {} assigned to the Optical Channel {}".format(name, och)
                logger.debug(msg)
                return jsonify(msg, 200)

            except Exception as e:
                logger.error(
                    "Logical channel assignation between Client {} and Optical Channel {} failed. Error: {}".format(
                        name, och, e))
                raise e
        else:
            return jsonify("Invalid parameters supplied", 400)


@app.route('/api/v1/openconfig/logical_channel_assignment/<client>', methods=['DELETE'])
def remove_logical_channel_assignment(client):
    """
    Client assignation to an Optical Channel
    ---
    delete:
    description: Remove logical assignations between the Client specified by client and Optical Channels assigned.
    produces:
    - application/json
    parameters:
    - name: client
      in: path
      description: Client ID
      required: true
    responses:
        200:
            description: Successful operation
        400:
            description: Internal Error
    """
    if request.method == 'DELETE':
        try:
            for i in range(len(agent.logical_associations)):
                assoc_id = agent.logical_associations[i]['id']
                cl_id = int(client.split('c')[1])  # client id numerical part
                if assoc_id == cl_id:   # if client was assigned
                    agent.api.deleteDACOSCOperationsById(assoc_id)

            msg = "Logical assignations assigned on the Client %s removed." % client
            logger.debug(msg)
            return jsonify(msg, 200)

        except Exception as e:
            msg = "Logical assignations assigned on the Client %s not removed. Error: {}".format(client, e)
            logger.error(msg)
            raise e


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
      example: {'frequency': '192300000', 'mode': '111', 'name': 'channel-1', 'power': '10.0', 'status': 'enabled',
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
            freq = params['frequency']
            mode = params['mode']
            name = params['name']
            power = params['power']
            status = params['status']
            type = params['type']
            try:
                result = configuration(name, freq, power, mode)
                msg = "Optical Channel {} configured with average BER = {}".format(name, result)
                logger.debug(msg)
                return jsonify(msg, 200)

            except Exception as e:
                logger.error("Optical Channel {} configuration failed. Error: {}".format(name, e))
                raise e
        else:
            return jsonify("The parameters sent are not correct", 400)


@app.route('/api/v1/openconfig/optical_channel/<och>', methods=['DELETE'])
def disconnect(och):
    """
    Optical Channel configuration
    ---
    delete:
    description: Disable Laser and Amplifier
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
            # Disable Amplifier
            agent.disable_amplifier()

            # Disable Laser
            agent.disable_laser()

            msg = "Optical Channel och%s configuration removed" % och
            logger.debug(msg)
            return jsonify(msg, 200)

        except Exception as e:
            msg = "Optical Channel och{} configuration not removed. Error: {}".format(och, e)
            logger.error(msg)
            raise e


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
        agent.amplifier_setup()

        # Laser setup
        och_id = int(och.split('-')[1])
        if och_id == 101 or och_id == 102:
            power_laser = power + agent.losses_laser
            agent.laser_setup(freq, power_laser)

        # DAC/OSC setup
        bn = np.array(np.ones(DAC.Ncarriers) * DAC.bps, dtype=int).tolist()
        En = np.array(np.ones(DAC.Ncarriers)).tolist()
        eq = "MMSE"

        result = agent.dac_setup(bn, En, eq)
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
    app.run(host='0.0.0.0', port=5001, debug=True, threaded=False)
