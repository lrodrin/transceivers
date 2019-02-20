import logging
from logging.handlers import RotatingFileHandler
from os import sys, path
from subprocess import Popen, PIPE

from flasgger import Swagger
from flask import Flask, request, jsonify

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from lib.dac.dac import DAC
from lib.osc.osc import OSC

app = Flask(__name__)
Swagger(app)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('werkzeug')
logger.setLevel(logging.DEBUG)


@app.route('/api/dac_osc_configuration', methods=['POST'])
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
    parameters:
    - name: conf_mode
      in: body
      type: integer
      description: Identify the configuration mode of the transceiver
      example: 0 for configuration 1 METRO, 1 for configuration 2 METRO and 2 for configuration 3 BLUESPACE
    - name: trx_mode
      in: body
      type: integer
      description: Identify the mode for the transceiver of OSC
      example: 0 for estimation mode or 1 for transmission mode
    - name: tx_ID
      in: body
      type: integer
      description: Identify the channel of the DAC to be used and the local files to use for storing data of each client
      example: 0 or 1 
    - name: rx_ID
      in: body
      type: integer
      description: Identify the channel of the OSC to be used and the local files to use for storing data of each client
      example: 0 or 1 
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
    if request.method == 'POST':
        try:
            params = request.json
            dac_configuration(params)
            osc_configuration(params)
            return jsonify("DAC and OSC was successfully configured", 200)

        except Exception as e:
            logger.error(e)
            return jsonify("ERROR: DAC and OSC was not successfully configured {}".format(e), 405)


@app.route('/api/dac_configuration', methods=['POST'])
def dac_configuration(params):
    """
    DAC configuration
    ---
    post:
    description: |
        DAC configuration performs DSP to create an OFDM signal and creates an OFDM signal and uploads
        it to the LEIA DAC
    consumes:
    - application/json
    produces:
    - application/json
    parameters:
    - name: conf_mode
      in: body
      type: integer
      description: Identify the configuration mode of the transceiver
      example: 0 for configuration 1 METRO, 1 for configuration 2 METRO and 2 for configuration 3 BLUESPACE
    - name: tx_ID
      in: body
      type: integer
      description: Identify the channel of the DAC to be used and the local files to use for storing data of each client
      example: 0 or 1 
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
        configuration = params['conf_mode']
        tx_id = params['tx_ID']
        bn = params['bn']
        En = params['En']

        tx = DAC()
        temp_file = open(DAC.temp_file, "w")
        msg = "DAC was successfully configured. Configuration mode used: {}. Channel used: {}\n".format(
            configuration, tx_id)

        logger.debug(
            "DAC configuration started\nRunning configuration mode {} with channel id {}".format(configuration, tx_id))
        if configuration == 0 or configuration == 2:  # Configuration 1 or configuration 3
            if tx_id == 0:
                try:
                    logger.debug("Enable Hi DAC channel")
                    seq = "1\n 0\n 0\n 0\n"  # Hi_en, Hq_en, Vi_en, Vq_en
                    run_dac_configuration(tx, tx_id, bn, En, temp_file, seq, DAC.leia_up_filename)
                    return jsonify(msg, 200)

                except Exception as e:
                    logger.error(e)
                    return jsonify("ERROR: %s" % e, 405)

            elif tx_id == 1:
                try:
                    logger.debug("Enable Hq DAC channel")
                    seq = "0\n 1\n 0\n 0\n"  # Hi_en, Hq_en, Vi_en, Vq_en
                    run_dac_configuration(tx, tx_id, bn, En, temp_file, seq, DAC.leia_down_filename)
                    return jsonify(msg, 200)

                except Exception as e:
                    logger.error(e)
                    return jsonify("ERROR: %s" % e, 405)

        elif configuration == 1:  # Configuration 2
            if tx_id == 0:
                try:
                    logger.debug("Enable Hi DAC channel")
                    seq = "1\n 0\n 0\n 0\n"  # Hi_en, Hq_en, Vi_en, Vq_en
                    run_dac_configuration(tx, tx_id, bn, En, temp_file, seq, DAC.leia_up_filename)
                    return jsonify(msg, 200)

                except Exception as e:
                    logger.error(e)
                    return jsonify("ERROR: %s" % e, 405)

            if tx_id == 1:
                try:
                    logger.debug("Enable Hq DAC channel")
                    seq = "0\n 1\n 0\n 0\n"  # Hi_en, Hq_en, Vi_en, Vq_en
                    run_dac_configuration(tx, tx_id, bn, En, temp_file, seq, DAC.leia_down_filename)
                    return jsonify(msg, 200)

                except Exception as e:
                    logger.error(e)
                    return jsonify("ERROR: %s" % e, 405)

        logger.debug("DAC configuration finished")

    else:
        return jsonify("The parameters sended by the agent are not correct.", 405)


def run_dac_configuration(tx, tx_id, bn, En, temp_file, leia_sequence, leia_file):
    """
    Run DAC configuration.

        - Generate a BitStream and creates the OFDM signal to be uploaded into Leia DAC.
        - Enable the DAC channel.
        - Call MATLAB program to process the OFDM signal uploaded to the Leia DAC.

    :param tx: DAC object
    :type tx: DAC
    :param tx_id: channel of the DAC
    :type tx_id: int
    :param bn: bits per symbol per subcarrier
    :type bn: int array of 512 positions
    :param En: power per subcarrier figure
    :type En: float array of 512 positions
    :param temp_file: file to save the generated OFDM signal to be uploaded to the Leia DAC
    :type temp_file: file 
    :param leia_sequence: sets 1 to the active Leia output and 0 to the remaining outputs
    :type leia_sequence: str
    :param leia_file: file with the generated OFDM signal to be uploaded to the LEIA DAC
    :type leia_file: str (Leia_DAC_up.m or Leia_DAC_down.m)
    """
    tx.transmitter(tx_id, bn, En)
    temp_file.write(leia_sequence)
    matlab = 'C:/Program Files/MATLAB/R2010bSP1/bin/matlab.exe'
    options = '-nodisplay -nosplash -nodesktop -wait'
    try:
        command = """{} {} -r "cd(fullfile('{}')), {}" """.format(matlab, options, DAC.folder, leia_file)
        proc = Popen(command, stdout=PIPE, stderr=PIPE)  # MATLAB call with file Leia_DAC_up.m or Leia_DAC_down.m
        out, err = proc.communicate()
        if proc.returncode == 0:
            logger.debug("MATLAB call {} succeeded, exit-code = {} returned".format(command, proc.returncode))
        else:
            logger.error(
                "MATLAB call {} failed, exit-code = {} returned, error = {}".format(command, proc.returncode, str(err)))

    except OSError as error:
        logger.error("Failed to execute MATLAB, error = %s" % error)


@app.route('/api/osc_configuration', methods=['POST'])
def osc_configuration(params):
    """
    OSC configuration
    ---
    post:
    description: |
        OSC configuration adquires and process the OFDM signal. Runs the selected OSC configuration in order to process
        the received OFDM signal and retrieve the original bitstream
    consumes:
    - application/json
    produces:
    - application/json
    parameters:
    - name: conf_mode
      in: body
      type: integer
      description: Identify the configuration mode of the transceiver
      example: 0 for configuration 1 METRO, 1 for configuration 2 METRO and 2 for configuration 3 BLUESPACE
    - name: trx_mode
      in: body
      type: integer
      description: Identify the mode of the transceiver. 0 for estimation mode or 1 for transmission mode
    - name: rx_ID
      in: body
      type: integer
      description: Identify the channel of the OSC to be used and the local files to use for storing data of each client
      example: 0 or 1 
    - name: bn
      in: body
      type: array
      description: Contains the bits per symbol per subcarrier
    - name: En
      in: body
      type: array
      description: Contains the power per subcarrier figure
    - name: equalitzation
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
        configuration = params['conf_mode']
        trx_mode = params['trx_mode']
        rx_id = params['rx_ID']
        bn = params['bn']
        En = params['En']
        eq = params['eq']

        rx = OSC()
        msg = "OSC was successfully configured. Configuration mode used: {}. Channel used: {}\n".format(
            configuration, rx_id)

        logger.debug(
            "OSC configuration started\nRunning configuration mode {} with OSC channel id {}".format(configuration,
                                                                                                     rx_id))
        msg_log = "Processing received data of user {}".format(rx_id)
        if configuration == 0 or configuration == 2:  # Configuration 1 or configuration 3
            try:
                logger.debug(msg_log)
                result = run_osc_configuration(rx, trx_mode, rx_id, bn, En, eq, msg)
                return jsonify(result, 200)

            except Exception as e:
                logger.error(e)
                return jsonify("ERROR: %s" % e, 405)

        elif configuration == 1:  # Configuration 2
            if rx_id == 0:
                try:
                    logger.debug(msg_log)
                    result = run_osc_configuration(rx, trx_mode, rx_id, bn, En, eq, msg)
                    return jsonify(result, 200)

                except Exception as e:
                    logger.error(e)
                    return jsonify("ERROR: %s" % e, 405)

            if rx_id == 1:
                try:
                    logger.debug(msg_log)
                    result = run_osc_configuration(rx, trx_mode, rx_id, bn, En, eq, msg)
                    return jsonify(result, 200)

                except Exception as e:
                    logger.error(e)
                    return jsonify("ERROR: %s" % e, 405)

        logger.debug("OSC configuration finished")

    else:
        return jsonify("The parameters sended by the agent are not correct.", 405)


def run_osc_configuration(rx, trx_mode, rx_id, bn, En, eq, msg):
    """
    Run OSC configuration.
    Adquires the OFDM signal and implents specific DSP to retrieve the original bitstream.
    It calculates the BER and SNR in order to evaluate the system performance

    :param rx: OSC object
    :type rx: OSC
    :param trx_mode: estimation mode or transmission mode
    :type trx_mode: int (0 for estimation mode or 1 for transmission mode)
    :param rx_id: channel of the OSC
    :type rx_id: int
    :param bn: bits per symbol per subcarrier
    :type bn: int array of 512 positions
    :param En: power per subcarrier figure
    :type En: float array of 512 positions
    :param eq: Identify the type of equalization (MMSE or ZF)
    :type eq: str
    :param msg: print message
    :type msg: str
    :return: estimated SNR per subcarrier and the BER of received data
    :rtype: list
    """
    params = rx.receiver(trx_mode, rx_id, bn, En, eq)
    if params[1] > 4.6e-3:  # optimal BER
        # logger.debug(msg + "SNR = {} and not optimal BER = {}".format(params[0], params[1]))
        logger.debug(msg + "not optimal BER = {}".format(params[1]))
    else:
        # logger.debug(msg + "SNR = {} and optimal BER = {}".format(params[0], params[1]))
        logger.debug(msg + "optimal BER = {}".format(params[1]))

    return params[1]


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
