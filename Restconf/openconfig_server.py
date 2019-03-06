import logging
from logging.handlers import RotatingFileHandler
from os import sys, path

from flasgger import Swagger
from flask import Flask, request
from flask.json import jsonify

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from agent_core import AgentCore

app = Flask(__name__)
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
    description: |
        Reference to the line-side optical channel that should carry the current logical channel element.
        Use this reference to exit the logical element stage
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
            description: Invalid input params
        405:
            description: Assignation exception
    """
    if request.method == 'POST':
        params = request.json
        if params is not None:
            c = params['client']
            och = params['och']
            try:
                msg = AgentCore.local_channel_assignment(c, och)
                logger.debug(msg)
                return jsonify(msg, 200)

            except Exception as e:
                error_msg = "Local channel assignation between client {} and optical channel {} failed. Error: {}".format(
                    c, och, e)
                logger.error(error_msg)
                return jsonify(error_msg, 405)
        else:
            return jsonify("The parameters sent are not correct", 400)


@app.route('/api/vi/openconfig/optical_channel', methods=['POST'])
def optical_channel_configuration():
    """
    Optical Channel Configuration
    ---
    post:
    description: Configuration of an Optical Channel by setting frequency, power. mode and port
    consumes:
    - application/json
    produces:
    - application/json
    parameters:
    - name: params
      in: body
      description: the client and the optical channel to be assigned
      example: {'och': 'och1', 'freq': 193.4e6, 'power': 0.4, 'mode': 'HD-FEC'}
      required: true
    responses:
        200:
            description: Successful configuration
        400:
            description: Invalid input params
        405:
            description: Configuration exception
    """
    if request.method == 'POST':
        params = request.json
        if params is not None:
            och = params['och']
            freq = params['freq']
            power = params['power']
            mode = params['mode']
            try:
                msg = AgentCore.optical_channel_configuration(och, freq, power, mode)
                logger.debug(msg)
                return jsonify(msg, 200)

            except Exception as e:
                error_msg = "Optical channel {} configuration failed. Error: {}".format(och, e)
                logger.error(error_msg)
                return jsonify(error_msg, 405)
        else:
            return jsonify("The parameters sent are not correct", 400)


def define_logger():
    """
    Create, formatter and add Handlers (RotatingFileHandler and StreamHandler) to the logger.
    """
    fileHandler = RotatingFileHandler('metro-haul/openconfig_server.log', maxBytes=10000000, backupCount=5)  # File Handler
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
