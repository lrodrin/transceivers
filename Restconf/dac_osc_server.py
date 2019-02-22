import logging

from logging.handlers import RotatingFileHandler
from os import sys, path
from subprocess import Popen, PIPE
from flasgger import Swagger
from flask import Flask, request, jsonify

OPTIMAL_BER = 4.6e-3

STATUS_CODE_200 = 200
STATUS_CODE_405 = 405

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from lib.dac.dac import DAC
from lib.osc.osc import OSC

app = Flask(__name__)
Swagger(app)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('werkzeug')
logger.setLevel(logging.DEBUG)


@app.route('/api/dac_osc', methods=['POST'])
def dac_osc_configuration():
    """
    DAC and OSC configuration
    ---
    post:
    description: |
        DAC and OSC configuration performs DSP to modulate/demodulate an OFDM signal
        DAC configuration creates an OFDM signal and uploads it to Leia DAC
        OSC configuration adquires the transmitted OFDM signal and perform DSP to retrieve the original datastream
    consumes:
    - application/json
    produces:
    - application/json
    parameters: # TODO
    - name: params
      in: body
      type: dict
      description: # TODO
      example: # TODO
    responses:
        200:
            description: "Successful operation"
        405:
            description: "Invalid input"
    """
    if request.method == 'POST':
        params = request.json
        if params is not None:
            dac_out = params['dac_out']
            osc_in = params['osc_in']
            try:
                dac_configuration(params)
                osc_configuration(params)
                return jsonify("DAC {} and OSC {} was successfully configured".format(dac_out, osc_in), STATUS_CODE_200)

            except Exception as e:
                logger.error(e)
                return jsonify(
                    "DAC {} and OSC {} was not successfully configured. Error: {}".format(dac_out, osc_in, e),
                    STATUS_CODE_405)
        else:
            return jsonify("The parameters sended by the agent are not correct.", STATUS_CODE_405)


@app.route('/api/dac', methods=['POST'])
def dac_configuration(params):
    """
    DAC configuration
    ---
    post:
    description: |
        DAC configuration performs DSP to create an OFDM signal and creates an OFDM signal and uploads
        it to the LEIA DAC
    produces:
    - application/json
    parameters:
    - name: dac_out
      in: body
      type: integer
      description: # TODO
    - name: bn
      in: body
      type: array
      description: Contains the bits per symbol per subcarrier
    - name: En
      in: body
      type: array
      description: Contains the power per subcarrier figure
    responses:
        200:
            description: "Successful operation"
        405:
            description: "Invalid input"
    """
    if params is not None:
        dac_out = params['dac_out']
        bn = params['bn']
        En = params['En']

        logger.debug("DAC {} configuration started".format(dac_out))
        try:
            logger.debug("Processing received data from %s" % dac_out)
            tx = DAC()
            tx.transmitter(dac_out, bn, En)
            return jsonify("DAC {} configuration finished".format(dac_out), STATUS_CODE_200)

        except Exception as e:
            logger.error(e)
            return jsonify("DAC {} configuration not finished. Error: {}".format(dac_out, e), STATUS_CODE_405)
    else:
        return jsonify("The parameters sended by the agent are not correct.", STATUS_CODE_405)


@app.route('/api/osc', methods=['POST'])
def osc_configuration(params):
    """
    OSC configuration
    ---
    post:
    description: |
        OSC configuration adquires and process the OFDM signal. Runs the selected OSC configuration in order to process
        the received OFDM signal and retrieve the original bitstream
    produces:
    - application/json
    parameters:
    - name: dac_out
      in: body
      type: integer
      description: Identify the input port of DAC associated
    - name: osc_in
      in: body
      type: integer
      description: Identify the output port
    - name: bn
      in: body
      type: array
      description: Contains the bits per symbol per subcarrier
    - name: En
      in: body
      type: array
      description: Contains the power per subcarrier figure
    - name: equalization
      in: body
      type: string
      description: Identify the equalization type
      example: MMSE or ZF
    responses:
        200:
            description: "Successful operation"
        405:
            description: "Invalid input"
    """
    if params is not None:
        dac_out = params['dac_out']
        osc_in = params['osc_in']
        bn = params['bn']
        En = params['En']
        eq = params['eq']

        logger.debug("OSC {} configuration started".format(osc_in))
        try:
            logger.debug("Processing received data from %s" % dac_out)
            rx = OSC()
            result = rx.receiver(osc_in, bn, En, eq)
            logger.debug("SNR = {} and BER = {}".format(result[0], result[1]))
            return jsonify(result, 200)

        except Exception as e:
            logger.error(e)
            return jsonify("OSC {} configuration not finished. Error: {}".format(osc_in, e), STATUS_CODE_405)
    else:
        return jsonify("The parameters sended by the agent are not correct.", STATUS_CODE_405)


def define_logger():
    """
    Create, formatter and add Handlers (RotatingFileHandler and StreamHandler) to the logger.
    """
    fileHandler = RotatingFileHandler('dac_osc_server.log', maxBytes=10000000, backupCount=5)  # File Handler
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
