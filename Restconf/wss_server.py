import collections
import logging
from logging.handlers import RotatingFileHandler
from os import sys, path

from flasgger import Swagger
from flask import Flask, request
from flask.json import jsonify

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from lib.wss.wss import WSS

app = Flask(__name__)
Swagger(app)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('werkzeug')
logger.setLevel(logging.DEBUG)

operations = collections.OrderedDict()


@app.route('/api/wss', methods=['POST'])
def wss_configuration():
    """
    WaveShaper configuration
    ---
    post:
    description: Sets the configuration file, central wavelength, bandwidth and attenuation/phase per port
    consumes:
    - application/json
    produces:
    - application/json
    parameters:
    - name: params
      in: body
      description: id to identify the WaveShaper and operations to be configured on the WaveShaper
      example: {'wss_id': 1, 'operations': [
        {'port_in': 1, 'port_out': 1, 'lambda0': 1550.52, 'att': 0.0, 'phase': 0.0, 'bw': 112.5}]}
      required: true
    responses:
        200:
            description: Successful configuration
        400:
            description: Invalid input params
    """
    if request.method == 'POST':
        params = request.json
        wss_id = str(params['wss_id'])
        ops = params['operations']
        if len(ops) != 0:
            logger.debug("WaveShaper %s configuration started" % wss_id)
            try:
                n, m = n_max(ops, 'port_in')
                wss = WSS(params['wss_id'], n, m)
                wss.configuration(ops)
                
                # Adding new operation
                if wss_id not in operations.keys():
                    operations[wss_id] = ops
                else:
                    operations[wss_id] += ops

                msg = "WaveShaper %s was successfully configured" % wss_id
                logger.debug(msg)
                return jsonify(msg, 200)

            except Exception as e:
                logger.error("WaveShaper {} wasn't successfully configured. Error: {}".format(wss_id, e))
                raise e

        else:
            return jsonify("The parameters sent are not correct", 400)


@app.route('/api/wss', methods=['GET'])
def wss_operations():
    """
    WaveShaper operations
    ---
    get:
    description: Get multiple operations configured on the WaveShapers
    produces:
    - application/json
    parameters:
    - name: operations
      in: query
      type: dict
      description: operations configured on the WaveShapers
    responses:
        200:
            description: Successful operation
            schema:
                type: dict
                example: {'wss_id': 1, 'operations': [
        {'port_in': 1, 'port_out': 1, 'lambda0': 1550.52, 'att': 0.0, 'phase': 0.0, 'bw': 112.5}]}
        404:
            description: Operations not found
    """
    if request.method == 'GET':
        if len(operations) != 0:    # If exists operations
            return jsonify(operations)
        else:
            return jsonify("Not exists operations", 404)


@app.route('/api/wss/<wss_id>', methods=['GET'])
def wss_getOperationsByID(wss_id):
    """
    WaveShaper operations by ID
    ---
    get:
    description: Returns operations configured on a WaveShaper specified by id
    produces:
    - application/json
    parameters:
    - name: wss_id
      in: path
      type: integer
      description: id of the WaveShaper
      required: true
    responses:
        200:
            description: Successful operation
            schema:
                type: dict
                example: {'wss_id': 1, 'operations': [
        {'port_in': 1, 'port_out': 1, 'lambda0': 1550.52, 'att': 0.0, 'phase': 0.0, 'bw': 112.5}]}
        400:
            description: Invalid ID supplied
        404:
            description: Operations not found
    """
    wss_id = str(wss_id)
    msg_not_exists_operations = "Not exists operations on the WaveShaper %s." % wss_id
    msg_not_exists = "Not exists operations"

    if request.method == 'GET':
        if len(operations) != 0:    # If exists operations
            if operations[wss_id]:  # If exists operations for wss_id
                return jsonify(wss_id, operations[wss_id])
            else:
                return jsonify(msg_not_exists_operations, 400)
        else:
            return jsonify(msg_not_exists, 404)


@app.route('/api/wss/<wss_id>', methods=['DELETE'])
def wss_deleteOperationsByID(wss_id):
    """
    WaveShaper operations by ID
    ---
    get:
    description: Delete operations configured on a WaveShaper specified by id
    produces:
    - application/json
    parameters:
    - name: wss_id
      in: path
      type: integer
      description: id of the WaveShaper
      example: 1
      required: true
    responses:
        200:
            description: Successful operation
        400:
            description: Invalid ID supplied
        404:
            description: Operations not found
    """
    wss_id = str(wss_id)
    msg_not_exists_operations = "Not exists operations on the WaveShaper %s." % wss_id
    msg_not_exists = "Not exists operations"

    if request.method == 'DELETE':
        if len(operations) != 0:    # If exists operations
            if operations[wss_id]:  # If exists operations for wss_id
                del operations[wss_id]
                return jsonify("Operations deleted for WaveShaper %s" % wss_id, 200)
            else:
                return jsonify(msg_not_exists_operations, 400)
        else:
            return jsonify(msg_not_exists, 404)


def n_max(ops, key_func):
    """
    Return the maximum element of input ports into operations.

    :param ops: operations to configure the WaveShaper
    :type ops: list
    :param key_func: comparison key
    :type key_func: str
    :return: maximum element of input ports
    :rtype: int
    """
    maximum = 0
    for i in range(len(ops)):
        if ops[i][key_func] > maximum:
            maximum = ops[i][key_func]
    return maximum


def define_logger():
    """
    Create, formatter and add Handlers (RotatingFileHandler and StreamHandler) to the logger.
    """
    fileHandler = RotatingFileHandler('wss_server.log', maxBytes=10000000, backupCount=5)  # File Handler
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
