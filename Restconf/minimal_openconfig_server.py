import logging
from logging.handlers import RotatingFileHandler
from os import sys, path

from flasgger import Swagger
from flask import Flask, request
from flask.json import jsonify
from flask_ini import FlaskIni

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

app = Flask(__name__)
app.iniconfig = FlaskIni()
Swagger(app)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('werkzeug')
logger.setLevel(logging.DEBUG)


@app.route('/api/vi/openconfig/local_channel_assignment', methods=['POST'])
def local_channel_assignment():
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
      description: the client and the optical channel to be assigned
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
                msg = "Client {} assigned to the Optical Channel {}".format(c, och)
                logger.debug(msg)
                return jsonify(msg, 200)

            except Exception as e:
                logger.error(
                    "Local channel assignation between client {} and optical channel {} failed. Error: {}".format(
                        c, och, e))
                raise e
        else:
            return jsonify("The parameters sent are not correct", 400)


@app.route('/api/vi/openconfig/local_channel_assignment/<client>', methods=['DELETE'])
def remove_local_channel_assignment(client):
    """
    Client assignation to an Optical Channel
    ---
    delete:
    description: Remove logical assignations between Client specified by client and Optical channels.
    produces:
    - application/json
    parameters:
    - name: client
      in: path
      description: id to identify the client
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
        # TODO search och assigned to client
        och = "och1"
        try:
            msg = "Client c{} assigned to the Optical Channel {} removed".format(client, och)
            logger.debug(msg)
            return jsonify(msg, 200)

        except Exception as e:
            msg = "Client c{} assigned to the Optical Channel {} not removed. Error: {}".format(client, och, e)
            logger.error(msg)
            return jsonify(msg, 404)


@app.route('/api/vi/openconfig/optical_channel', methods=['POST'])
def optical_channel():
    """
    Optical Channel configuration
    ---
    post:
    description: Configuration of an optical channel by setting frequency, power and mode.
    consumes:
    - application/json
    produces:
    - application/json
    parameters:
    - name: params
      in: body
      description: parameters of the Optical Channel to be configured
      example: {'och': 'och1', 'freq': 193.4e6, 'power': 0.4, 'mode': 'HD-FEC'}
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
            och = params['och']
            freq = params['freq']
            power = params['power']
            mode = params['mode']
            try:
                msg = "Optical Channel {} configured with frequency = {}, power = {} and mode = {}".format(och, freq,
                                                                                                           power, mode)
                logger.debug(msg)
                return jsonify(msg, 200)

            except Exception as e:
                logger.error("Optical Channel {} configuration failed. Error: {}".format(och, e))
                raise e
        else:
            return jsonify("The parameters sent are not correct", 400)


@app.route('/api/vi/openconfig/optical_channel/<och>', methods=['DELETE'])
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
      description: id that identify the optical channel to be removed
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
