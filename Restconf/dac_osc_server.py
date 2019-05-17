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

logging.basicConfig(level=logging.DEBUG)  # import logging from DAC and OSC
logger = logging.getLogger('werkzeug')
logger.setLevel(logging.DEBUG)

logical_associations = collections.OrderedDict()  # logical associations between DAC and OSC database


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
    - name: body
      in: body
      description: logical association to be configured between DAC and OSC
      schema:
        type: array
        example: [{'id': 1, 'dac_out': 1, 'osc_in': 2, 'bn': bn, 'En': En, 'eq': eq}]
      required: true
    responses:
        200:
            description: Successful configuration
            schema:
                type: array
                example: [[], 0.0004997929791905]
        400:
            description: Internal Error
    """
    if request.method == 'POST':
        logic_assoc = request.json
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
                dac_configuration(dac_out, bn, En)  # DAC configuration
                [SNR, BER] = osc_configuration(dac_out, osc_in, bn, En, eq)  # OSC configuration

                # Adding new logical association to database
                filtered_assoc = dict(
                    zip(wanted_keys,
                        [logic_assoc[index][k] for k in wanted_keys]))  # logic_assoc - logic_assoc['id']
                if assoc_id not in logical_associations.keys():
                    logical_associations[assoc_id] = filtered_assoc

                logger.debug(
                    "DAC and OSC logical association with id: %s was successfully added" % assoc_id)

            except Exception as e:
                logger.error(
                    "DAC and OSC logical association with id: {} wasn't successfully added. Error: {}".format(
                        assoc_id, e))
                raise e

            logger.debug("DAC and OSC was successfully configured")
            return jsonify([SNR, BER])


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
    description: Get logical associations configured between DAC and OSC
    produces:
    - application/json
    parameters:
    - name: logical associations
      in: query
      description: logical association configured between DAC and OSC
    responses:
        200:
            description: Successful operation
            schema:
                type: array
                example: [{'id': 1, 'dac_out': 1, 'osc_in': 2, 'bn': bn, 'En': En, 'eq': eq}]
        400:
            description: Internal Error
    """
    if request.method == 'GET':
        if len(logical_associations) != 0:  # If exists logical associations
            return jsonify(logical_associations)
        else:
            return jsonify("Not exists logical association between DAC and OSC.", 400)


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
      description: id that identifies a logical association
      required: true
    responses:
        200:
            description: Successful operation
            schema:
                type: array
                example: [{'id': 1, 'dac_out': 1, 'osc_in': 2, 'bn': bn, 'En': En, 'eq': eq}]
        400:
            description: Invalid ID supplied
    """
    assoc_id = str(assoc_id)
    if request.method == 'GET':
        if len(logical_associations) != 0:  # If exists association
            if logical_associations[assoc_id]:  # If exists association for assoc_id
                return jsonify(assoc_id, logical_associations[assoc_id])
            else:
                return jsonify("Not exists logical association between DAC and OSC with id %s." % assoc_id, 400)


@app.route('/api/dac_osc/<assoc_id>', methods=['DELETE'])
def dac_osc_deleteAssociationByID(assoc_id):
    """
    DAC and OSC logical association by ID
    ---
    delete:
    description: Remove logical association configured between DAC and OSC specified by id
    produces:
    - application/json
    parameters:
    - name: assoc_id
      in: path
      type: integer
      description: iid that identifies a logical association
      required: true
    responses:
        200:
            description: Successful operation
        400:
            description: Invalid ID supplied
    """
    assoc_id = str(assoc_id)
    if request.method == 'DELETE':
        if len(logical_associations) != 0:  # If exists association
            if logical_associations[assoc_id]:  # If exists association for assoc_id
                del logical_associations[assoc_id]
                return jsonify("Logical association %s deleted" % assoc_id, 200)
            else:
                return jsonify("Not exists logical association between DAC and OSC with id %s." % assoc_id, 400)


def configure_logger():
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
    configure_logger()
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=False)
