import logging
import os
import subprocess
import time

from flask import Flask, request, redirect, url_for, jsonify
from logging.handlers import RotatingFileHandler
from os import sys, path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from lib.dac.dac import DAC
from lib.osc.osc import OSC

OPTIMAL_BER = 4.6e-3
DAC_MATLAB_CALL_WITH_LEIA_DAC_DOWN = '"C:/Program Files/MATLAB/R2010bSP1/bin/matlab.exe" -nodisplay -nosplash ' \
                                     '-nodesktop -r '"Leia_DAC_down;"  # TODO

DAC_MATLAB_CALL_WITH_LEIA_DAC_UP = '"C:/Program Files/MATLAB/R2010bSP1/bin/matlab.exe" -nodisplay -nosplash ' \
                                   '-nodesktop -r '"Leia_DAC_up;"  # TODO

app = Flask(__name__)


@app.route('/api/hello', methods=['GET'])
def hello_world():  # TODO delete route
    if request.method == 'GET':
        try:
            logger.info('This is a info message!')
            logger.debug('This is a debug message!')
            logger.error('This is a error message!')
            logger.warning('This is a warning message!')
            return jsonify('Hello, World!', 200)

        except Exception as e:
            logger.error(e)
            raise e


@app.route('/api/hello2', methods=['GET'])
def hello_world2():  # TODO delete route
    if request.method == 'GET':
        try:
            return redirect(url_for('hello_world'))

        except Exception as e:
            logger.error(e)
            raise e


@app.route('/api/dac', methods=['POST'])
def dac_startup():
    """
    DAC route.

    post:
        summary: DAC configuration.
        description: Startup DAC configuration.
            - Configuration 1:
                - To demonstrate bidirectionality.
                - Simple scheme: An OpenConfig terminal device comprises BVTx+BVTRx of a single client.
                - There are two Openconfig Terminals (C1 and C2).
            - Configuration 2:
                - The S-BVT consist of 2 clients (C1 and C2) that are part of a single OpenConfig terminal device.
                - Two clients are assigned to a single optical channel, corresponding to two logical optical channels,
                creating a superchannel. The central wavelength of the superchannel is configured/set by the OpenConfig
                agent.
                - We can not demonstrate bidirectionality due to hardware limitations.
            - Configuration 3: # TODO BLUESPACE

        attributes:
            - name: conf_mode
              description: Identify the configuration mode of the transceiver.
              type: int (0 for configuration 1 METRO, 1 for configuration 2 METRO and 2 for configuration 3 BLUESPACE).
            - name: tx_ID
              description: Identify the channel of the DAC to be used and the local files to use for storing data.
              type: int (0 or 1)
            - name: bn
              description: Contains the bits per symbol per subcarrier.
              type: int array of 512 positions
            - name: En
              description: Contains the power per subcarrier figure.
              type: float array of 512 positions

        responses:
            200:
                description: (str, int, int) DAC was successfully configured. Shows the type of configuration and the
                channel of the DAC used.
            500:
                description: (str) Error message in case there is some error.
    """
    if request.method == 'POST':
        params = request.json  # conf_mode, tx_ID, bn, En values from agent
        if params is not None:
            configuration = params['conf_mode']
            tx_id = params['tx_ID']
            bn = params['bn']
            En = params['En']

            tx = DAC()
            temp_file = open(DAC.temp_file, "w")
            msg = "DAC was successfully configured. Configuration mode used: {}. Channel used: {}\n".format(
                configuration, tx_id)

            logger.debug("Running configuration mode {} with DAC channel id {}".format(configuration, tx_id))
            if configuration == 0 or configuration == 2:  # Configuration 1 or configuration 3
                if tx_id == 0:
                    try:
                        logger.debug("Enable Hi DAC channel")
                        seq = "1\n 0\n 0\n 0\n"  # Hi_en, Hq_en, Vi_en, Vq_en
                        run_dac_configuration(tx, tx_id, bn, En, temp_file, seq, "UP")
                        return jsonify(msg, 200)

                    except Exception as e:
                        logger.error(e)
                        return jsonify(e, 500)

                elif tx_id == 1:
                    try:
                        logger.debug("Enable Hq DAC channel")
                        seq = "0\n 1\n 0\n 0\n"  # Hi_en, Hq_en, Vi_en, Vq_en
                        run_dac_configuration(tx, tx_id, bn, En, temp_file, seq, "DOWN")
                        return jsonify(msg, 200)

                    except Exception as e:
                        logger.error(e)
                        return jsonify(e, 500)

            elif configuration == 1:  # Configuration 2
                if tx_id == 0:
                    try:
                        logger.debug("Enable Hi DAC channel")
                        seq = "1\n 0\n 0\n 0\n"  # Hi_en, Hq_en, Vi_en, Vq_en
                        run_dac_configuration(tx, tx_id, bn, En, temp_file, seq, "UP")
                        return jsonify(msg, 200)

                    except Exception as e:
                        logger.error(e)
                        return jsonify(e, 500)

                if tx_id == 1:
                    try:
                        logger.debug("Enable Hq DAC channel")
                        seq = "0\n 1\n 0\n 0\n"  # Hi_en, Hq_en, Vi_en, Vq_en
                        run_dac_configuration(tx, tx_id, bn, En, temp_file, seq, "DOWN")
                        return jsonify(msg, 200)

                    except Exception as e:
                        logger.error(e)
                        return jsonify(e, 500)
        else:
            raise ValueError('The parameters sended by the agent are not correct.')


def run_dac_configuration(tx, tx_id, bn, En, temp_file, seq, leia_file):
    """
    Run DAC configuration.

        - Generate a BitStream and creates the OFDM signal to be uploaded into the DAC.
        - Enable the DAC channel.
        - Call MATLAB program to process ? # TODO

    :param tx: DAC object
    :type tx: DAC
    :param tx_id: channel of the DAC
    :type tx_id: int
    :param bn: bits per symbol per subcarrier
    :type bn: int array of 512 positions
    :param En: power per subcarrier figure
    :type En: float array of 512 positions
    :param temp_file: # TODO
    :type temp_file: file
    :param seq: # TODO
    :type seq: str
    :param leia_file: # TODO
    :type leia_file: str
    """
    tx.transmitter(tx_id, bn, En)
    try:
        temp_file.write(seq)
        if leia_file == "UP":  # TODO change to subprocess
            os.system(DAC_MATLAB_CALL_WITH_LEIA_DAC_UP)  # MATLAB call with file Leia_DAC_up.m
        else:
            os.system(DAC_MATLAB_CALL_WITH_LEIA_DAC_DOWN)  # MATLAB call with file Leia_DAC_down.m

        time.sleep(DAC.sleep_time)

    except Exception as error:
        logger.error(error)
        raise error


@app.route('/api/osc', methods=['POST'])
def osc_startup():
    """
    OSC route.

    post:
        summary: OSC configuration.
        description: Startup OSC configuration.
            - Configuration 1:
                - To demonstrate bidirectionality.
                - Simple scheme: An OpenConfig terminal device comprises BVTx+BVTRx of a single client.
                - There are two Openconfig Terminals (C1 and C2).
            - Configuration 2:
                - The S-BVT consist of 2 clients (C1 and C2) that are part of a single OpenConfig terminal device.
                - Two clients are assigned to a single optical channel, corresponding to two logical optical channels,
                creating a superchannel. The central wavelength of the superchannel is configured/set by the OpenConfig
                agent.
                - We can not demonstrate bidirectionality due to hardware limitations.
            - Configuration 3: # TODO BLUESPACE

        attributes:
            - name: conf_mode
              description: Identify the configuration mode of the transceiver.
              type: int (0 for configuration 1 METRO, 1 for configuration 2 METRO and 2 for configuration 3 BLUESPACE)
            - name: trx_mode
              description: Identify the mode of the transceiver.
              type: int (0 for estimation mode or 1 for transmission mode)
            - name: rx_ID
              description: Identify the channel of the OSC to be used and the local files to use for storing data.
              type: int (0 or 1)
             name: bn
              description: Contains the bits per symbol per subcarrier.
              type: int array of 512 positions
            - name: En
              description: Contains the power per subcarrier figure.
              type: float array of 512 positions
            - name: eq
              description: # TODO
              type: # TODO

        responses:
            200:
                description:
                    - (str, int, int) OSC was successfully configured.  Shows the type of configuration and the
                    channel of the OSC used.
                    - (float array of 512 positions) that contains the estimated SNR per subcarrier.
                    - (float array of 512 positions) that contains the BER of received data.
            500:
                description: (str) Error message in case there is some error.
    """
    if request.method == 'POST':
        params = request.json  # conf_mode, trx_mode, rx_ID, bn, En, eq values from agent
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

            logger.debug("Running configuration mode {} with channel id {}".format(configuration, rx_id))
            if configuration == 0:   # Configuration 1
                try:
                    logger.debug("")   # TODO
                    result = run_osc_configuration(rx, trx_mode, rx_id, bn, En, eq, msg)
                    return jsonify(result, 200)

                except Exception as e:
                    logger.error(e)
                    return jsonify(e, 500)

            elif configuration == 1:
                if rx_id == 0:
                    try:
                        logger.debug("")  # TODO
                        result = run_osc_configuration(rx, trx_mode, rx_id, bn, En, eq, msg)
                        return jsonify(result, 200)

                    except Exception as e:
                        logger.error(e)
                        return jsonify(e, 500)

                if rx_id == 1:
                    try:
                        logger.debug("")  # TODO
                        result = run_osc_configuration(rx, trx_mode, rx_id, bn, En, eq, msg)
                        return jsonify(result, 200)

                    except Exception as e:
                        logger.error(e)
                        return jsonify(e, 500)

            elif configuration == 2:  # TODO BLUESPACE
                pass
        else:
            raise ValueError('The parameters sended by the agent are not correct.')


def run_osc_configuration(rx, trx_mode, rx_id, bn, En, eq, msg):
    """
    Run OSC configuration.
    # TODO more description

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
    :param eq: # TODO
    :type eq: # TODO
    :param msg: print message
    :type msg: str
    :return: print message with estimated SNR per subcarrier and the BER of received data
    :rtype: str
    """
    snr, ber = rx.receiver(trx_mode, rx_id, bn, En, eq)
    if ber > OPTIMAL_BER:
        return msg + "SNR = {} and not optimal BER = {}".format(snr, ber)
    else:
        return msg + "SNR = {} and optimal BER = {}".format(snr, ber)


if __name__ == '__main__':
    # File Handler
    fileHandler = RotatingFileHandler('server/server.log', maxBytes=10000000, backupCount=5)
    # Stream Handler
    streamHandler = logging.StreamHandler()
    # Create a Formatter for formatting the logs messages
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(filename)s: %(message)s")
    # TODO Add formatter
    # Add the Formatter to the Handler
    # fileHandler.setFormatter(formatter)
    # streamHandler.setFormatter(formatter)
    # Create the Logger
    logger = logging.getLogger('werkzeug')
    logger.setLevel(logging.DEBUG)
    # Add Handlers to the Logger
    logger.addHandler(fileHandler)
    logger.addHandler(streamHandler)
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=False)
