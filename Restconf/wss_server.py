import logging
from collections import Counter
from logging.handlers import RotatingFileHandler
from os import sys, path

from flasgger import Swagger
from flask import Flask, request
from flask.json import jsonify

STATUS_CODE_200 = 200
STATUS_CODE_405 = 405

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from lib.wss.wss import WSS

app = Flask(__name__)
Swagger(app)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('werkzeug')
logger.setLevel(logging.DEBUG)


@app.route('/api/wss', methods=['POST'])
def wss_configuration():
    """
    WaveShaper configuration
    ---
    post:
    description: |
        WaveShaper configuration. This function sets the configuration file, central wavelength, bandwidth and
        attenuation/phase per port to the WaveShaper module. And saves the operations to be configured on the WaveShaper
    consumes:
    - application/json
    produces:
    - application/json
    parameters:
    - name: wss_id
      in: body
      type: integer
      description: Identifies the WaveShaper
      example: 1 or 2
    - name: operations
      in: body
      type: list of dictionaries
      description: Operations to be configured on the WaveShaper identified by id
    responses:
        200:
            description: "Successful operation"
        405:
            description: "Invalid input"
    """
    if request.method == 'POST':
        params = request.json
        if params is not None:
            wss_id = params['wss_id']
            operations = params['operation']
            try:
                n, m = calculateNandM(operations)
                wss_tx = WSS(wss_id, n, m)
                wss_tx.configuration(operations)

                if wss_id not in WSS.operations.keys():  # Adding new operation
                    WSS.operations[wss_id] = operations
                else:
                    WSS.operations[wss_id] += operations

                return jsonify("WaveShaper %s was successfully configured" % wss_id, STATUS_CODE_200)

            except Exception as e:
                logger.error(e)
                return jsonify("WaveShaper {} not was successfully configured. Error: {}".format(wss_id, e),
                               STATUS_CODE_405)
        else:
            return jsonify("The parameters sended by the agent are not correct.", STATUS_CODE_405)


@app.route('/api/wss', methods=['GET'])  # TODO attach into the POST
def wss_operations():
    """
    WaveShaper operations
    ---
    get:
    description: Get operations from a set of WaveShapers
    produces:
    - application/json
    responses:
        200:
            description: "Successful operation"
        405:
            description: "Invalid value"
        """
    if request.method == 'GET':
        if len(WSS.operations) != 0:
            return jsonify(WSS.operations)
        else:
            return jsonify("Not exists any WaveShaper configurated", STATUS_CODE_405)


@app.route('/api/wss/<wss_id>', methods=['GET', 'DELETE'])
def wss_operations(wss_id):
    """
    WaveShaper operations by id
    ---
    get:
    description: Get or delete operations that configure a WaveShaper specified by id
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
        405:
            description: "Invalid value"
        """
    wss_id = str(wss_id)
    msg_not_exists_operations = "Not exists operations on the WaveShaper %s." % wss_id
    msg_not_exists_waveshapers = "Not exists any WaveShaper configured"
    if request.method == 'GET':
        if len(WSS.operations) != 0:
            if WSS.operations[wss_id]:
                return jsonify(wss_id, WSS.operations[wss_id])
            else:
                return jsonify(msg_not_exists_operations, STATUS_CODE_405)
        else:
            return jsonify(msg_not_exists_waveshapers, STATUS_CODE_405)

    elif request.method == 'DELETE':
        if len(WSS.operations) != 0:
            if WSS.operations[wss_id]:
                del WSS.operations[wss_id]
                return jsonify(wss_id, WSS.operations[wss_id])
            else:
                return jsonify(msg_not_exists_operations, STATUS_CODE_405)
        else:
            return jsonify(msg_not_exists_waveshapers, STATUS_CODE_405)


def calculateNandM(operations):
    """
    Calculate the total number of input and output ports of a WaveShaper.

    :param operations: operations that configure a WaveShaper
    :type operations: list
    :return: number of input (n) and output ports (m)
    :rtype: int, int
    """
    n = Counter()
    m = Counter()
    for op in operations:
        n[op["port_in"]] += 1
        m[op["port_out"]] += 1

    logger.debug("Number of input ports = {} and number of output ports {}".format(n, m))
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
