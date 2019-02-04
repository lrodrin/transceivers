import logging
import os
import time

from logging.handlers import RotatingFileHandler

from flask import Flask, request, json, Response, redirect, url_for
from os import sys, path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from lib.dac.dac import DAC
from lib.osc.osc import OSC

OPTIMAL_BER = 4.6e-3  # HD-FEC
DAC_MATLAB_CALL_WITH_LEIA_DAC_DOWN = '"C:/Program Files/MATLAB/R2010bSP1/bin/matlab.exe" -nodisplay -nosplash ' \
                                     '-nodesktop -r '"Leia_DAC_down;"  # TODO link to file

DAC_MATLAB_CALL_WITH_LEIA_DAC_UP = '"C:/Program Files/MATLAB/R2010bSP1/bin/matlab.exe" -nodisplay -nosplash ' \
                                   '-nodesktop -r '"Leia_DAC_up;"  # TODO link to file

app = Flask(__name__)


# -r "cd(fullfile('/Users/Jules/Dropbox/CODES/Matlab/')), coverGUI_AL_FOV"


@app.route('/api/hello', methods=['GET'])
def hello_world():  # TODO esborrar quan fucnioni tot
    log.info('This is a info message!')
    log.debug('This is a debug message!')
    log.error('This is a error message!')
    log.warning('This is a warning message!')
    return Response(response=json.dumps('Hello, World!'), status=200, mimetype='application/json')


@app.route('/api/hello2', methods=['GET'])
def hello_world2():  # TODO esborrar quan fucnioni tot
    return redirect(url_for('hello_world'))


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
                - There are two Openconfig Terminals (C1 and C2)
            - Configuration 2:
                - The S-BVT consist of 2 clients (C1 and C2) that are part of a single OpenConfig terminal device.
                - Two clients are assigned to a single optical channel, corresponding to two logical optical channels,
                creating a superchannel. The central wavelength of the superchannel is configured/set by the OpenConfig
                agent.
                - We can not demonstrate bidirectionality due to hardware limitations.
            - Configuration 3: # TODO bluespace

        attributes:
            - name: trx_mode
              description: Identify the configuration mode of the transceiver.
              type: int (0 for configuration 1 METRO, 1 for configuration 2 METRO and 2 for configuration 3 BLUESPACE).
            - name: tx_ID
              description: Identify the channel of the DAC to be used and the local files to use for storing data.
              type: int (0 or 1)
            - name: FEC
              description: Identify the channel encoding to be used (TBI).
              type: str (HD-FEC or SD-FEC)
            - name: bps
              description: Contains the bits per symbol per subcarrier.
              type: int array of 512 positions
            - name: pps
              description: Contains the power per subcarrier figure.
              type: float array of 512 positions

        responses:
            200:
                description: (str, int, int) DAC was successfully configured. And the type of configuration done.
            404:
                description: (str) Error message in case there is some error.
    """
    # TODO extreure metode amb codi repetit
    payload = request.json  # trx_mode, tx_ID, FEC, bps, pps values from agent
    trx_mode = payload['trx_mode']
    tx_id = payload['tx_ID']
    fec = payload['FEC']
    bps = payload['bps']
    pps = payload['pps']

    tx = DAC()
    temp_file = open(DAC.temp_file, "w")
    ok_message = "DAC was successfully configured. Configuration mode: {}, {}\n".format(trx_mode, tx_id)
    if trx_mode == 0 or trx_mode == 2:  # Configuration 1 METRO and configuration 3 BLUESPACE
        try:
            tx.transmitter(trx_mode, tx_id, fec, bps, pps)
            if tx_id == 0:
                temp_file.write("1\n 0\n 0\n 0\n")  # Hi_en, Hq_en, Vi_en, Vq_en
                os.system(DAC_MATLAB_CALL_WITH_LEIA_DAC_UP)  # MATLAB call with file Leia_DAC_up.m
            elif tx_id == 1:
                temp_file.write("0\n 1\n 0\n 0\n")  # Hi_en, Hq_en, Vi_en, Vq_en
                os.system(DAC_MATLAB_CALL_WITH_LEIA_DAC_DOWN)  # MATLAB call with file Leia_DAC_down.m

            time.sleep(DAC.sleep_time)
            return log.debug(ok_message)

        except OSError as error:
            return log.debug("ERROR: {} \n".format(error))

    elif trx_mode == 1:  # Configuration 2 METRO
        try:
            if tx_id == 0:
                tx.transmitter(trx_mode, tx_id, fec, bps, pps)
                temp_file.write("1\n 0\n 0\n 0\n")  # Hi_en, Hq_en, Vi_en, Vq_en
                os.system(DAC_MATLAB_CALL_WITH_LEIA_DAC_UP)  # MATLAB call with file Leia_DAC_up.m
                time.sleep(DAC.sleep_time)
                return log.debug(ok_message)

            try:
                if tx_id == 1:
                    tx.transmitter(trx_mode, tx_id, fec, bps, pps)
                    temp_file.write("0\n 1\n 0\n 0\n")  # Hi_en, Hq_en, Vi_en, Vq_en
                    os.system(DAC_MATLAB_CALL_WITH_LEIA_DAC_DOWN)  # MATLAB call with file Leia_DAC_down.m
                    time.sleep(DAC.sleep_time)
                    return log.debug(ok_message)

            except OSError as error:
                return log.debug("ERROR: {} \n".format(error))

        except OSError as error:
            return log.debug("ERROR: {} \n".format(error))


@app.route('/api/osc', methods=['POST'])
def osc_startup():
    """
    OSC route.

    post:
        summary: OSC configuration.
        description: Startup OSC configuration.
            - Configuration 1:
            - Configuration 2:
            - Configuration 3: bluespace

        attributes:
            - name: rx_ID
              description: Identify the channel of the OSC to be used and the local files to use for storing data.
              type: int (0 or 1)
            - name: trx_mode
              description: Identify the mode of the transceiver.
              type: int (0 for estimation mode or 1 for transmission mode)
            - name: FEC
              description: Identify the channel encoding to be used (TBI).
              type: str (HD-FEC or SD-FEC)
            - name: bps
              description: Contains the bits per symbol per subcarrier.
              type: int array of 512 positions
            - name: pps
              description: Contains the power per subcarrier figure.
              type: float array of 512 positions

        responses:
            200:
                description:
                    - (string, int, int) OSC was successfully configured. And the type of configuration done.
                    - (float array of 512 positions) that contains the estimated SNR per subcarrier.
                    - (float) the BER of received data.
            404:
                description: (string) Error message in case there is some error.
    """
    payload = request.json  # trx_mode, rx_ID, FEC, bps, pps values from agent
    scenario = payload['trx_mode']
    rx_id = payload['rx_ID']
    fec = payload['FEC']
    bps = payload['bps']
    pps = payload['pps']

    is_optimal = False
    rx = OSC(scenario, rx_id, fec, bps, pps)
    if scenario == 0:
        try:
            result = rx.receiver()
            if result[1] > OPTIMAL_BER:
                return print_ok_message(is_optimal, result, rx_id, scenario)
            else:
                is_optimal = True
                return print_ok_message(is_optimal, result, rx_id, scenario)

        except OSError as error:
            return log.debug("ERROR: {} \n".format(error))

    elif scenario == 1:
        try:
            if rx_id == 0:
                result = rx.receiver()
                if result[1] > OPTIMAL_BER:
                    return print_ok_message(is_optimal, result, rx_id, scenario)
                else:
                    is_optimal = True
                    return print_ok_message(is_optimal, result, rx_id, scenario)
            try:
                if rx_id == 1:
                    result = rx.receiver()
                    if result[1] > OPTIMAL_BER:
                        return print_ok_message(is_optimal, result, rx_id, scenario)
                    else:
                        is_optimal = True
                        return print_ok_message(is_optimal, result, rx_id, scenario)

            except OSError as error:
                return log.debug("ERROR: {} \n".format(error))

        except OSError as error:
            return log.debug("ERROR: {} \n".format(error))

    elif scenario == 2:  # bluespace
        try:
            result = rx.receiver()
            if result[1] > OPTIMAL_BER:
                return print_ok_message(is_optimal, result, rx_id, scenario)
            else:
                is_optimal = True
                return print_ok_message(is_optimal, result, rx_id, scenario)

        except OSError as error:
            return log.debug("ERROR: {} \n".format(error))


@app.route('/api/dac_and_osc_configuration', methods=['POST'])
def dac_and_osc_configuration():
    # TODO passar els paramatres
    redirect(url_for('dac_startup'))
    redirect(url_for('osc_startup'))


def print_ok_message(is_optimal, result, rx_id, scenario):
    """
    Print the ouput from receiver method.

    :param is_optimal: optimal BER
    :param result: SNR and BER
    :param rx_id: receiver id
    :param scenario: type of configuration
    :type is_optimal: bool
    :type result: list
    :type rx_id: int
    :type scenario: int
    :return: Ok message
    :rtype: str
    """
    message = "Oscilloscope was successfully configured with SNR {} and {} BER {}\n Configuration type: {}, {}\n"
    if is_optimal:
        return log.debug(message.format(result[0], "optimal", result[1], scenario, rx_id))
    else:
        return log.debug(message.format(result[0], "no optimal", result[1], scenario, rx_id))


if __name__ == '__main__':
    # File Handler
    fileHandler = RotatingFileHandler('server.log', maxBytes=10000000, backupCount=5)
    # Stream Handler
    streamHandler = logging.StreamHandler()
    # Create a Formatter for formatting the log messages
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(filename)s: %(message)s")
    # TODO Add formatter
    # Add the Formatter to the Handler
    # fileHandler.setFormatter(formatter)
    # streamHandler.setFormatter(formatter)
    # Create the Logger
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.DEBUG)
    # Add Handlers to the Logger
    log.addHandler(fileHandler)
    log.addHandler(streamHandler)
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=False)
