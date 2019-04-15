import argparse
import ast
import logging
from logging.handlers import RotatingFileHandler
from os import sys, path

from flasgger import Swagger
from flask import Flask, request
from flask.json import jsonify
from flask_ini import FlaskIni

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from agent_core import AgentCore

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


@app.route('/api/vi/openconfig/local_channel_assignment', methods=['POST'])
def local_channel_assignment():
    """
    Client assignation to an Optical Channel
    ---
    post:
    description: |
        Reference to the line-side optical channel that should carry the current logical channel element.
        Use this reference to exit the logical element stage.
    consumes:
    - application/json
    produces:
    - application/json
    parameters:
    - name: params
      in: body
      description: the client and the Optical Channel to be assigned
      example: {'client': 'c1', 'och': 'och1'}
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
            c = params['client']
            och = params['och']
            try:
                msg = ac.logical_channel_assignment(c, och)
                logger.debug(msg)
                return jsonify(msg, 200)

            except Exception as e:
                logger.error(
                    "Local channel assignation between client {} and optical channel {} failed. Error: {}".format(
                        c, och, e))
                raise e
        else:
            return jsonify("The parameters sent are not correct", 400)


@app.route('/api/vi/openconfig/optical_channel', methods=['POST'])
def optical_channel():
    """
    Optical Channel configuration
    ---
    post:
    description: Configuration of an Optical Channel by setting frequency, power and mode.
    consumes:
    - application/json
    produces:
    - application/json
    parameters:
    - name: params
      in: body
      description: the client and the Optical Channel to be assigned
      example: {'och': 'och1', 'freq': 193.4e6, 'power': 0.4, 'mode': 'HD-FEC'}
      required: true
    responses:
        200:
            description: Successful configuration
        400:
            description: Invalid input parameters for an Optical Channel
    """
    if request.method == 'POST':
        params = request.json
        if len(params) != 0:
            och = params['och']
            freq = params['freq']
            power = params['power']
            mode = params['mode']
            try:
                result = ac.optical_channel(och, freq, power, mode)
                logger.debug("Optical channel {} configured with average BER = {}".format(och, result[1]))
                return jsonify(msg, 200)

            except Exception as e:
                logger.error("Optical channel {} configuration failed. Error: {}".format(och, e))
                raise e
        else:
            return jsonify("The parameters sent are not correct", 400)


@app.route('/api/vi/openconfig/optical_channel<och>', methods=['DELETE'])
def remove_optical_channel(och):
    """
    Optical Channel configuration
    ---
    delete:
    description: Remove configuration of an Optical Channel specified by id
    produces:
    - application/json
    parameters:
    - name: och
      in: path
      type: integer
      description: id of Optical Channel
      required: true
    responses:
        200:
            description: Successful operation
        400:
            description: Invalid ID supplied
        404:
            description: Association not found
    """
    if request.method == 'DELETE':
        try:
            ac.remove_optical_channel()
            msg = "Optical Channel deleted"
            logger.debug(msg)
            return jsonify(msg, 200)

        except Exception as e:
            msg = "Optical Channel not deleted. Error: %s" % e
            logger.error(msg)
            return jsonify(msg, 404)


def define_logger():
    """
    Create, formatter and add Handlers (RotatingFileHandler and StreamHandler) to the logger.
    """
    fileHandler = RotatingFileHandler('openconfig_server.log', maxBytes=10000000,
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
