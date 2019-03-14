import collections
import logging
from logging.handlers import RotatingFileHandler
from os import sys, path

from flasgger import Swagger
from flask import Flask, request
from flask.json import jsonify

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from lib.dac.dac import DAC
from lib.osc.osc import OSC

app = Flask(__name__)
Swagger(app)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('werkzeug')
logger.setLevel(logging.DEBUG)

logical_associations = collections.OrderedDict()


@app.route('/api/dac_osc', methods=['POST'])
def dac_osc_configuration():
    """
    DAC and OSC configuration
    ---
    post:
    description: |
        DAC and OSC configuration performs DSP to modulate/demodulate an OFDM signal.
        DAC configuration creates an OFDM signal and uploads it to Leia DAC.
        OSC configuration adquires the transmitted OFDM signal and perform DSP to retrieve the original datastream.
    consumes:
    - application/json
    produces:
    - application/json
    parameters:
    - name: logical_assoc
      in: body
      description: logical association to be configured between DAC and OSC
      example: [{'id': 1, 'dac_out': 1, 'osc_in': 2, 'bn': bn1, 'En': En1, 'eq': eq1},
              {'id': 2, 'dac_out': 2, 'osc_in': 1, 'bn': bn2, 'En': En2, 'eq': eq2}]
      required: true
    responses:
        200:
            description: Successful configuration
            schema:
                type: list
                example: [SNR, BER]
        400:
            description: Invalid input logical_assoc
    """
    if request.method == 'POST':
        logic_assoc = request.json
        if len(logic_assoc) != 0:
            logger.debug("DAC and OSC configuration started")
            wanted_keys = ('dac_out', 'osc_in', 'bn', 'En', 'eq')
            for index in range(len(logic_assoc)):  # for each logic association between DAC and OSC
                assoc_id = str(logic_assoc[index]['id'])
                dac_out = logic_assoc[index]['dac_out']
                osc_in = logic_assoc[index]['osc_in']
                bn = logic_assoc[index]['bn']
                En = logic_assoc[index]['En']
                eq = logic_assoc[index]['eq']

                try:
                    dac_configuration(dac_out, bn, En)
                    [SNR, BER] = osc_configuration(dac_out, osc_in, bn, En, eq)
                    logger.debug("SNR = {}\nBER = {}".format(SNR, BER))

                    # Adding new logical association
                    filtered_assoc = dict(
                        zip(wanted_keys,
                            [logic_assoc[index][k] for k in wanted_keys]))  # logic_assoc - logic_assoc['id']
                    if assoc_id not in logical_associations.keys():
                        logical_associations[assoc_id] = filtered_assoc

                    logger.debug(
                        "DAC and OSC logical association with id: %s was successfully configured" % assoc_id)

                except Exception as e:
                    logger.error(
                        "DAC and OSC logical association with id: {} wasn't successfully configured. Error: {}".format(
                            assoc_id, e))
                    raise e

            return jsonify("DAC and OSC was successfully configured")
        
        else:
            return jsonify("The parameters sent are not correct", 400)


def dac_configuration(dac_out, bn, En):
    """
    DAC configuration.

        - Creates an OFDM signal and uploads it to Leia DAC.
        - Enable DAC channel.
        - Call MATLAB program to process the OFDM signal uploaded to the Leia DAC.

    :param dac_out: output port of DAC
    :type dac_out: int
    :param bn: contains the bits per symbol per subcarrier
    :type bn: list of floats
    :param En: contains the power per subcarrier figure
    :type En: list of floats
    """
    logger.debug("DAC configuration started")
    try:
        logger.debug("Processing data from DAC output port: %s" % dac_out)
        tx = DAC()
        temp_file = open(DAC.temp_file, "w")
        tx.transmitter(dac_out, bn, En)
        leia_file = tx.enable_channel(dac_out, temp_file)
        tx.execute_matlab(leia_file)
        logger.debug("DAC configuration finished")

    except Exception as e:
        logger.error("DAC configuration not finished. Error: {}".format(e))
        raise e


def osc_configuration(dac_out, osc_in, bn, En, eq):
    """
    OSC configuration adquires the transmitted OFDM signal and perform DSP to retrieve the original datastream.

    :param dac_out: output port of DAC
    :type dac_out: int
    :param osc_in: input port of OSC
    :type osc_in: int
    :param bn: contains the bits per symbol per subcarrier
    :type bn: list of floats
    :param En: contains the power per subcarrier figure
    :type En: list of floats
    :param eq: identify the equalization MMSE or ZF
    :type eq: str
    :return: estimated SNR per subcarrier and the BER of received data
    :rtype: list
    """
    logger.debug("OSC configuration started")
    try:
        logger.debug("Processing data from OSC input port: %s" % osc_in)
        rx = OSC()
        [SNR, BER] = rx.receiver(dac_out, osc_in, bn, En, eq)
        logger.debug("OSC configuration finished")
        return [SNR, BER]

    except Exception as e:
        logger.error("OSC configuration not finished. Error: {}".format(e))
        raise e


@app.route('/api/dac_osc', methods=['GET'])
def dac_osc_associations():
    """
    DAC and OSC logical associations
    ---
    get:
    description: Get multiple logical associations configured between DAC and OSC
    produces:
    - application/json
    parameters:
    - name: associations
      in: query
      type: list
      description: logical associations configured between DAC and OSC
    responses:
        200:
            description: Successful operation
            schema:
                type: list
                example: [{'id': 1, 'dac_out': 1, 'osc_in': 2, 'bn': bn1, 'En': En1, 'eq': eq1},
              {'id': 2, 'dac_out': 2, 'osc_in': 1, 'bn': bn2, 'En': En2, 'eq': eq2}]
        404:
            description: Associations not found
    """
    if request.method == 'GET':
        if len(logical_associations) != 0:  # If exists associations
            return jsonify(logical_associations)
        else:
            return jsonify("Not exists operations", 404)


@app.route('/api/dac_osc/<assoc_id>', methods=['GET'])
def dac_osc_getAssociationByID(assoc_id):
    """
    DAC and OSC logical association by ID
    ---
    get:
    description: Returns logical association configured between DAC and OSC specified by id
    produces:
    - application/json
    parameters:
    - name: assoc_id
      in: path
      type: integer
      description: id of logical association configured between DAC and OSC
      required: true
    responses:
        200:
            description: Successful operation
            schema:
                type: list
                example: [{'id': 1, 'dac_out': 1, 'osc_in': 2, 'bn': bn1, 'En': En1, 'eq': eq1},
              {'id': 2, 'dac_out': 2, 'osc_in': 1, 'bn': bn2, 'En': En2, 'eq': eq2}]
        400:
            description: Invalid ID supplied
        404:
            description: Association not found
    """
    assoc_id = str(assoc_id)
    msg_not_exists_associations = "Not exists logical association between DAC and OSC with id %s." % assoc_id
    msg_not_exists = "Not exists logical associations"

    if request.method == 'GET':
        if len(logical_associations) != 0:  # If exists association
            if logical_associations[assoc_id]:  # If exists association for assoc_id
                return jsonify(assoc_id, logical_associations[assoc_id])
            else:
                return jsonify(msg_not_exists_associations, 400)
        else:
            return jsonify(msg_not_exists, 404)


@app.route('/api/dac_osc/<assoc_id>', methods=['DELETE'])
def dac_osc_deleteAssociationByID(assoc_id):
    """
    DAC and OSC logical association by ID
    ---
    delete:
    description: Delete logical association configured between DAC and OSC specified by id
    produces:
    - application/json
    parameters:
    - name: assoc_id
      in: path
      type: integer
      description: id of logical association configured between DAC and OSC
      required: true
    responses:
        200:
            description: Successful operation
        400:
            description: Invalid ID supplied
        404:
            description: Association not found
    """
    assoc_id = str(assoc_id)
    msg_not_exists_associations = "Not exists logical association between DAC and OSC with id %s." % assoc_id
    msg_not_exists = "Not exists logical associations"

    if request.method == 'DELETE':
        if len(logical_associations) != 0:  # If exists association
            if logical_associations[assoc_id]:  # If exists association for assoc_id
                del logical_associations[assoc_id]
                return jsonify("Logical association %s deleted" % assoc_id, 200)
            else:
                return jsonify(msg_not_exists_associations, 400)
        else:
            return jsonify(msg_not_exists, 404)


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
