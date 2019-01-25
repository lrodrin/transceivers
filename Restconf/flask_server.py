import os
import time

from flask import Flask, request
from os import sys, path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from lib.dac.dac import DAC, DAC_INPUTS_ENABLE_FILE, SLEEP_TIME
from lib.osc.osc import OSC

OPTIMAL_BER = 4.6e-3
DAC_MATLAB_CALL_WITH_LEIA_DAC_DOWN = '"C:/Program Files/MATLAB/R2010bSP1/bin/matlab.exe" -nodisplay -nosplash ' \
                                     '-nodesktop -r '"Leia_DAC_down; "  # TODO link to file

DAC_MATLAB_CALL_WITH_LEIA_DAC_UP = '"C:/Program Files/MATLAB/R2010bSP1/bin/matlab.exe" -nodisplay -nosplash ' \
                                   '-nodesktop -r '"Leia_DAC_up; "  # TODO link to file

app = Flask(__name__)


@app.route('/api/hello', methods=['GET'])
def hello_world():  # TODO esborrar quan fucnioni tot
    return 'Hello, World!'


@app.route('/api/dac', methods=['POST'])
def dac_startup():
    """
    DAC route.

    post:
        summary: DAC configuration.
        description: Startup DAC configuration.
            - Configuration 1a:
                - To demonstrate bidirectionality.
                - Simple scheme: An OpenConfig terminal device comprises BVTx+BVTRx of a single client.
            - Configuration 1b:
                - The S-BVT architecture is used for a single client creating a superchannel.
                - Up to 2 slices can be enabled to increase data rate according to the bandwith requirements.
                - The superchannel central wavelength is configured/set by the OpenConfig agent.
            - Configuration 2:
                - The S-BVT consist of 2 clients (C1 and C2) that are part of a single OpenConfig terminal device.
                - There is another S-BVT with 2 more clients (C3, C4) or a BVT with a single client C3 at another point
                  of the network that corresponds to another OpenConfig terminal.
                - The superchannel central wavelength is configured/set by the OpenConfig agent.
                - Two clients are assigned to a single optical channel, corresponding to two logical optical channels.
                - We can not demonstrate bidirectionality due to hardware limitations.
            - Configuration 3: # TODO bluespace

        attributes:
            - name: trx_mode
              description: Identify the configuration mode of the transceiver.
              type: int (0 for configuration 1a and 1b scenario or 1 for configuration 1 scenario or 2 for
              configuration 3).
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
                description: (string, int, int) DAC was successfully configured. And the type of configuration done.
            404:
                description: (string) Error message in case there is some error.

    """
    payload = request.json  # trx_mode, tx_ID, FEC, bps, pps values from agent
    scenario = payload['trx_mode']
    tx_id = payload['tx_ID']
    fec = payload['FEC']
    bps = payload['bps']  # always 2 value from METRO
    pps = payload['pps']

    tx = DAC(scenario, tx_id, fec, bps, pps)
    f = open(DAC_INPUTS_ENABLE_FILE, "w")
    file_uploaded_message = 'Leia initialized and SPI file uploaded'
    ok_message = "DAC was successfully configured. Configuration type: {}, {}\n".format(scenario, tx_id)
    if scenario == 0:  # Configuration 1
        try:
            tx.transmitter()
            if tx_id == 0:  # Configuration 1a
                f.write("1\n 0\n 0\n 0\n")  # Hi_en, Hq_en, Vi_en, Vq_en
                os.system(DAC_MATLAB_CALL_WITH_LEIA_DAC_UP)  # MATLAB call with file Leia_DAC_up.m

            else:  # Configuration 1b
                f.write("0\n 1\n 0\n 0\n")  # Hi_en, Hq_en, Vi_en, Vq_en
                os.system(DAC_MATLAB_CALL_WITH_LEIA_DAC_DOWN)  # MATLAB call with file Leia_DAC_down.m

            time.sleep(SLEEP_TIME)
            print(file_uploaded_message)
            return ok_message

        except OSError as error:
            return "ERROR: {} \n".format(error)

    elif scenario == 1:  # Configuration 2
        try:
            if tx_id == 0:
                # TODO extract method run_dac_configuration
                tx.transmitter()
                f.write("1\n 0\n 0\n 0\n")  # Hi_en, Hq_en, Vi_en, Vq_en
                os.system(DAC_MATLAB_CALL_WITH_LEIA_DAC_UP)  # MATLAB call with file Leia_DAC_up.m
                time.sleep(SLEEP_TIME)
                print(file_uploaded_message)
                return ok_message

            try:
                if tx_id == 1:
                    tx.transmitter()
                    f.write("0\n 1\n 0\n 0\n")  # Hi_en, Hq_en, Vi_en, Vq_en
                    os.system(DAC_MATLAB_CALL_WITH_LEIA_DAC_DOWN)  # MATLAB call with file Leia_DAC_down.m
                    time.sleep(SLEEP_TIME)
                    print(file_uploaded_message)
                    return ok_message

            except OSError as error:
                return "ERROR: {} \n".format(error)

        except OSError as error:
            return "ERROR: {} \n".format(error)

    # elif scenario == 3: # Configuration 3 # TODO bluespace


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
                is_optimal = True
                return print_ok_message(is_optimal, result, rx_id, scenario)
            else:  # TODO this case?
                return print_ok_message(is_optimal, result, rx_id, scenario)

        except OSError as error:
            return "ERROR: {} \n".format(error)

    elif scenario == 1:
        try:
            if rx_id == 0:
                # TODO extract method run_osc_configuration
                result = rx.receiver()
                if result[1] > OPTIMAL_BER:
                    is_optimal = True
                    return print_ok_message(is_optimal, result, rx_id, scenario)
                else:
                    return print_ok_message(is_optimal, result, rx_id, scenario)
            try:
                if rx_id == 1:
                    result = rx.receiver()
                    if result[1] > OPTIMAL_BER:
                        is_optimal = True
                        return print_ok_message(is_optimal, result, rx_id, scenario)
                    else:
                        return print_ok_message(is_optimal, result, rx_id, scenario)

            except OSError as error:
                return "ERROR: {} \n".format(error)

        except OSError as error:
            return "ERROR: {} \n".format(error)

    elif scenario == 2:  # bluespace
        try:
            result = rx.receiver()
            if result[1] > OPTIMAL_BER:
                is_optimal = True
                return print_ok_message(is_optimal, result, rx_id, scenario)
            else:
                return print_ok_message(is_optimal, result, rx_id, scenario)

        except OSError as error:
            return "ERROR: {} \n".format(error)


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
        return message.format(result[0], "optimal", result[1], scenario, rx_id)
    else:
        return message.format(result[0], "no optimal", result[1], scenario, rx_id)


if __name__ == '__main__':
    # app.run(host='10.1.1.10', port=5000, debug=True)  # REAL
    app.run(host='127.0.0.1', port=5000, debug=True)  # TEST
