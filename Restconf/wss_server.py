import logging
from logging.handlers import RotatingFileHandler

from flasgger import Swagger
from flask import Flask, request
from os import sys, path

from flask.json import jsonify

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
        attenuation/phase per port to the waveshaper module.
    consumes:
    - application/json
    produces:
    - application/json
    parameters:
    - name: WaveShaper id
      in: body
      type: integer
      description: Identifies the WaveShaper
      example: 1 or 2
    - name: operation
      in: body
      type: list of dictionaries
      description: Operations to be configured on the WaveShaper
      example: [{'port_in': 1, 'port_out': 1, 'lambda0': 1550.12, 'att': 0.0, 'phase': 0.0, 'bw': 25}]
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
            operation = params['operation']
            try:
                wss_tx = WSS(wss_id, len(operation), 1)  # TODO m = 1
                wss_tx.configuration(operation)
                return jsonify("WaveShaper %s was successfully configured" % wss_id, 200)

            except Exception as e:
                logger.error(e)
                return jsonify("WaveShaper {} not was successfully configured. Error: {}".format(wss_id, e), 405)
        else:
            return jsonify("The parameters sended by the agent are not correct.", 405)


@app.route('/api/wss/<wss_id>', methods=['GET'])
def wss_operations(wss_id):
    """
    WaveShaper operations
    ---
    get:
    description: Multiple operations that configure the WaveShaper specified by wss_id
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
    if request.method == 'GET':
        if len(WSS.operations) != 0:
            if WSS.operations[wss_id]:
                return jsonify(wss_id, WSS.operations[wss_id])
            else:
                return jsonify("Not exists operations for the WaveShaper %s." % wss_id, 405)
        else:
            return jsonify("Not exists any WaveShaper configurated", 405)


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
