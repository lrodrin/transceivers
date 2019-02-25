import collections
import logging
from collections import Counter
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


@app.route('/api/wss', methods=['POST', 'GET'])
def wss_configuration():
    """
    WaveShaper configuration
    ---
    post:
    description: |
        WaveShaper configuration. This function sets the configuration file, central wavelength, bandwidth and
        attenuation/phase per port to the WaveShaper module.
    consumes:
    - application/json
    produces:
    - application/json
    parameters:
    - name: wss_id
      in: body
      type: integer
      description: Identifies the WaveShaper
    - name: ops
      in: body
      type: list of dictionaries
      description: Operation to be configured on the WaveShaper
    responses:
        200:
            description: "Successful operation"
        405:
            description: "Invalid input"
    get:
    description: Get operations configured on a set of WaveShaper
    produces:
    - application/json
    responses:
        200:
            description: "Successful operation" # TODO
        404:
            description: "WaveShaper not found" # TODO
    """
    if request.method == 'POST':
        params = request.json
        if params is not None:
            wss_id = str(params['wss_id'])
            ops = params['operation']
            try:
                n, m = calculateNxM(ops)
                wss = WSS(params['wss_id'], n, m)
                wss.configuration(ops)

                # Adding new operation
                if wss_id not in operations.keys():
                    operations[wss_id] = ops
                else:
                    operations[wss_id] += ops

                return jsonify("WaveShaper %s was successfully configured" % wss_id, 200)

            except Exception as e:
                logger.error(e)
                return jsonify("WaveShaper {} not was successfully configured. Error: {}".format(wss_id, e),
                               405)
        else:
            return jsonify("The parameters send by the agent are not correct.", 405)

    elif request.method == 'GET':
        if len(operations) != 0:
            return jsonify(operations)
        else:
            return jsonify("Not exists operations on any WaveShaper")


@app.route('/api/wss/<wss_id>', methods=['GET', 'DELETE'])
def wss_operations(wss_id):
    """
    WaveShaper operations
    ---
    get:
    description: Get operations configured on a WaveShaper specified by id
    produces:
    - application/json
    parameters:
    - name: wss_id
      in: body
      type: integer
      description: Identifies the WaveShaper
    responses:
        200:
            description: "Successful operation"
        400:
            description: "Invalid ID supplied"
    delete:
    description: Delete operations configured on a WaveShaper specified by id
    produces:
    - application/json
    parameters:
    - name: wss_id
      in: body
      type: integer
      description: Identifies the WaveShaper
    responses:
        200:
            description: "Successful operation" # TODO
        400:
            description: "Invalid ID supplied" # TODO
        404:
            description: "WaveShaper not found" # TODO
    """
    wss_id = str(wss_id)
    msg_not_exists_operations = "Not exists operations on the WaveShaper %s." % wss_id
    msg_not_exists_waveshaper = "WaveShaper %s not configured" % wss_id

    if request.method == 'GET':
        if len(operations) != 0:
            if operations[wss_id]:
                return jsonify(wss_id, operations[wss_id])
            else:
                return jsonify(msg_not_exists_operations, 400)
        else:
            return jsonify(msg_not_exists_waveshaper, 404)

    elif request.method == 'DELETE':
        if len(operations) != 0:
            if operations[wss_id]:
                del operations[wss_id]
                return jsonify("WaveShaper %s operations deleted." % wss_id, 200)
            else:
                return jsonify(msg_not_exists_operations, 400)
        else:
            return jsonify(msg_not_exists_waveshaper, 404)


def calculateNxM(operation):
    """
    Calculate the total number of input and output ports of an operation.

    :param operation: operation that configure a WaveShaper
    :type operation: list
    :return: number of input (n) and output ports (m)
    :rtype: int, int
    """
    n = Counter()
    m = Counter()
    for op in operation:
        n[op["port_in"]] += 1
        m[op["port_out"]] += 1

    logger.debug("Number of input ports = {} and number of output ports {}".format(len(n), len(m)))
    return len(n), len(m)


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
