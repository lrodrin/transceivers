import collections
import logging
from logging.handlers import RotatingFileHandler
from os import sys, path

from flasgger import Swagger
from flask import Flask, request, jsonify

OPTIMAL_BER = 4.6e-3

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from lib.dac.dac import DAC
from lib.osc.osc import OSC

app = Flask(__name__)
Swagger(app)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('werkzeug')
logger.setLevel(logging.DEBUG)

logical_associations = collections.OrderedDict()


@app.route('/api/dac_osc', methods=['GET', 'POST'])
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
        - name: logical_assoc
          in: body
          type: list of dictionaries
          description: Logical association to be configured between DAC and OSC
          example: [{'id': 1, 'dac_out': 1, 'osc_in': 1, 'bn': bn, 'En': En, 'eq': 0}]
        responses:
            200:
                description: "Successful operation"
            405:
                description: "Invalid input"
    get:
        description: Get all the logical associations configured between DAC and OSC
        produces:
        - application/json
        responses:
            200:
                description: "Successful operation" # TODO
            404:
                description: "Logical associations between DAC and OSC not found" # TODO
    """
    if request.method == 'POST':
        logic_assoc = request.json
        if len(logic_assoc) != 0:
            wanted_keys = ('dac_out', 'osc_in', 'bn', 'En', 'eq')
            try:
                for index in range(len(logic_assoc)):  # for each logic association between DAC and OSC
                    assoc_id = str(logic_assoc[index]['id'])
                    dac_out = logic_assoc[index]['dac_out']
                    osc_in = logic_assoc[index]['osc_in']
                    bn = logic_assoc[index]['bn']
                    En = logic_assoc[index]['En']
                    eq = logic_assoc[index]['eq']

                    dac_configuration(dac_out, bn, En)
                    osc_configuration(dac_out, osc_in, bn, En, eq)

                    # Adding new logical association
                    filtered_assoc = dict(
                        zip(wanted_keys, [logic_assoc[index][k] for k in wanted_keys]))  # logic_assoc - ['id']
                    if assoc_id not in logical_associations.keys():
                        logical_associations[assoc_id] = filtered_assoc

                return jsonify("DAC and OSC was successfully configured", 200)

            except Exception as e:
                logger.error(e)
                return jsonify("DAC and OSC was not successfully configured. Error: {}".format(e), 405)
        else:
            return jsonify("Empty parameters send by the agent.", 405)

    elif request.method == 'GET':
        if len(logical_associations) != 0:
            return jsonify(logical_associations)
        else:
            return jsonify("Not exists any logical association between DAC and OSC")


def dac_configuration(dac_out, bn, En):
    """
    DAC configuration.
    Performs DSP to create an OFDM signal and creates an OFDM signal and uploads it to the LEIA DAC.

    :param dac_out: identify the output port of DAC
    :type dac_out: int
    :param bn: contains the bits per symbol per subcarrier
    :type bn: list of floats
    :param En: contains the power per subcarrier figure
    :type En: list of floats
    """
    logger.debug("DAC {} configuration started".format(dac_out))
    try:
        logger.debug("Processing received data from %s" % dac_out)
        tx = DAC()
        temp_file = open(DAC.temp_file, "w")
        tx.transmitter(dac_out, bn, En)
        leia_file = tx.enable_channel(dac_out, temp_file)
        if leia_file is not None:
            tx.execute_matlab(leia_file)
        logger.debug("DAC {} configuration finished".format(dac_out))

    except Exception as e:
        logger.error("DAC {} configuration not finished. Error: {}".format(dac_out, e))
        raise e


def osc_configuration(dac_out, osc_in, bn, En, eq):
    """
    OSC configuration.
    Adquires and process the OFDM signal. Runs the selected OSC configuration in order to process the received OFDM
    signal and retrieve the original bitstream.

    :param dac_out: identify the output port of DAC
    :type dac_out: int
    :param osc_in: identify the input port of OSC
    :type osc_in: int
    :param bn: contains the bits per symbol per subcarrier
    :type bn: list of floats
    :param En: contains the power per subcarrier figure
    :type En: list of floats
    :param eq: identify the equalization type (MMSE or ZF)
    :type eq: str
    """
    logger.debug("OSC {} configuration started".format(osc_in))
    try:
        logger.debug("Processing received data from %s" % dac_out)
        rx = OSC()
        result = rx.receiver(dac_out, osc_in, bn, En, eq)
        # logger.debug("SNR = {} and BER = {}".format(result[0], result[1]))
        logger.debug("BER = {}".format(result[1]))
        logger.debug("OSC {} configuration finished".format(osc_in))
        return jsonify(result[1], 200)

    except Exception as e:
        logger.error("OSC {} configuration not finished. Error: {}".format(osc_in, e))
        raise e


@app.route('/api/dac_osc/<assoc_id>', methods=['GET', 'DELETE'])
def dac_osc_logical_associations(assoc_id):
    """
    DAC and OSC logical association
    ---
    get:
        description: Get logical association configured between DAC and OSC specified by id
        produces:
        - application/json
        parameters:
        - name: assoc_id
          in: body
          type: integer
          description: Identifies the logical association configured between DAC and OSC
        responses:
            200:
                description: "Successful operation"
            400:
                description: "Invalid ID supplied"
    delete:
        description: Delete logical association configured between DAC and OSC specified by id
        produces:
        - application/json
        parameters:
        - name: assoc_id
          in: body
          type: integer
          description: Identifies the logical association configured between DAC and OSC
        responses:
            200:
                description: "Successful operation" # TODO
            400:
                description: "Invalid ID supplied" # TODO
            404:
                description: "Logical associations between DAC and OSC not found" # TODO
    """
    assoc_id = str(assoc_id)
    msg_not_exists_associations = "Not exists logical associations between DAC and OSC with id %s." % assoc_id
    msg_not_configured_association = "Logical association %s between DAC and OSC not configured" % assoc_id

    if request.method == 'GET':
        if len(logical_associations) != 0:
            if logical_associations[assoc_id]:
                return jsonify(assoc_id, logical_associations[assoc_id])
            else:
                return jsonify(msg_not_exists_associations, 400)
        else:
            return jsonify(msg_not_configured_association, 404)

    elif request.method == 'DELETE':
        if len(logical_associations) != 0:
            if logical_associations[assoc_id]:
                del logical_associations[assoc_id]
                return jsonify("WaveShaper %s operations deleted." % assoc_id, 200)
            else:
                return jsonify(msg_not_exists_associations, 400)
        else:
            return jsonify(msg_not_configured_association, 404)


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
