import os
import time

from flask import Flask, request
from os import sys, path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from lib.dac.dac import DAC, METRO_DAC_INPUTS_ENABLE_FILE, SLEEP_TIME

METRO_DAC_MATLAB_CALL_WITH_LEIA_DAC_DOWN = '"C:/Program Files/MATLAB/R2010bSP1/bin/matlab.exe" -nodisplay -nosplash ' \
                                           '-nodesktop -r '"Leia_DAC_down; "    # TODO link to file

METRO_DAC_MATLAB_CALL_WITH_LEIA_DAC_UP = '"C:/Program Files/MATLAB/R2010bSP1/bin/matlab.exe" -nodisplay -nosplash ' \
                                         '-nodesktop -r '"Leia_DAC_up; "    # TODO link to file

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

app = Flask(__name__)


@app.route('/api/hello', methods=['GET'])
def hello_world():  # TODO esborrar quan fucnioni tot
    return 'Test: Hello, World!'


@app.route('/api/blue/dac', methods=['POST'])
def blue_dac():
    """
    DAC Bluespace route.

    post:
        summary: Bluespace DAC configuration.
        description: Startup Bluespace DAC configuration.
        attributes:
            - name: tx_ID
              description: Identify the channel of the DAC to be used and the local files to use for storing data.
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
                description: (int) 0 for OK.
            404:
                description: (int) -1 in case there is some error.

    """
    payload = request.json  # tx_ID, trx_mode, FEC, bps, pps values from agent
    try:
        ack = transmitter(payload['tx_ID'], payload['trx_mode'], payload['FEC'], payload['bps'], payload['pps'])
        return "DAC ACK {}\n".format(ack)

    except OSError as error:
        return "ERROR: {} \n".format(error)


@app.route('/api/blue/osc', methods=['POST'])
def blue_osc():
    """
    OSC Bluespace route.

    post:
        summary: Bluespace OSC configuration.
        description: Startup Bluespace OSC configuration.
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
                    - (int) 0 for OK.
                    - (float array of 512 positions) that contains the estimated SNR per subcarrier.
                    - (float) the BER of received data.
            404:
                description: (int) -1 in case there is some error.

    """
    payload = request.json  # rx_ID, trx_mode, FEC, bps, pps values from agent
    try:
        result = receiver(payload['rx_ID'], payload['trx_mode'], payload['FEC'], payload['bps'], payload['pps'])
        return "Oscilloscope ACK {} SNR {} BER {}\n".format(result[0], result[1], result[2])

    except OSError as error:
        return "ERROR: {} \n".format(error)


@app.route('/api/metro/dac', methods=['POST'])
def metro_dac():
    """
    DAC Metro-haul route.

    post:
        summary: Metro-haul DAC configuration.
        description: Startup Metro-haul DAC configuration.
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

        attributes:
            - name: trx_mode
              description: Identify the configuration mode of the transceiver.
              type: int (0 for configuration 1a and 1b scenario or 1 for configuration 1 scenario)
            - name: tx_ID
              description: Identify the channel of the DAC to be used and the local files to use for storing data.
              type: int (0 or 1)

        responses:
            200:
                description: (int) 0 for OK.
            404:
                description: (int) -1 in case there is some error.

    """
    payload = request.json  # trx_mode, tx_ID, SNR_estimation values from agent
    scenario = payload['trx_mode']
    channel_id = payload['tx_ID']

    tx = DAC(scenario, channel_id)
    f = open(METRO_DAC_INPUTS_ENABLE_FILE, "w")
    file_uploaded_message = 'Leia initialized and SPI file uploaded'
    if scenario == 0:  # Configuration 1
        try:
            ack = tx.transmitter()
            if channel_id == 0:  # Configuration 1a
                f.write("1\n 0\n 0\n 0\n")  # Hi_en, Hq_en, Vi_en, Vq_en
                os.system(METRO_DAC_MATLAB_CALL_WITH_LEIA_DAC_UP)  # MATLAB call with file Leia_DAC_up.m

            else:  # Configuration 1b
                f.write("0\n 1\n 0\n 0\n")  # Hi_en, Hq_en, Vi_en, Vq_en
                os.system(METRO_DAC_MATLAB_CALL_WITH_LEIA_DAC_DOWN)  # MATLAB call with file Leia_DAC_down.m

            time.sleep(SLEEP_TIME)
            print(file_uploaded_message)
            return "DAC ACK {}\n".format(ack)

        except OSError as error:
            return "ERROR: {} \n".format(error)

    elif scenario == 1:  # Configuration 2
        try:
            if channel_id == 0:
                # TODO extract method metro_dac_configuration_2
                ack = tx.transmitter()
                f.write("1\n 0\n 0\n 0\n")  # Hi_en, Hq_en, Vi_en, Vq_en
                os.system(METRO_DAC_MATLAB_CALL_WITH_LEIA_DAC_UP)  # MATLAB call with file Leia_DAC_up.m
                time.sleep(SLEEP_TIME)
                print(file_uploaded_message)
                return "DAC ACK {}\n".format(ack)

            if channel_id == 1:
                ack = tx.transmitter()
                f.write("0\n 1\n 0\n 0\n")  # Hi_en, Hq_en, Vi_en, Vq_en
                os.system(METRO_DAC_MATLAB_CALL_WITH_LEIA_DAC_DOWN)  # MATLAB call with file Leia_DAC_down.m
                time.sleep(SLEEP_TIME)
                print(file_uploaded_message)
                return "DAC ACK {}\n".format(ack)

        except OSError as error:
            return "ERROR: {} \n".format(error)


@app.route('/api/metro/osc', methods=['POST'])
def metro_osc():
    """
    OSC Metro-haul route.

    post:
        summary: Metro-haul DAC configuration.
        description: Startup Metro-haul OSC configuration.
        attributes:
            - name: rx_ID
              description: Identify the channel of the OSC to be used and the local files to use for storing data.
              type: int (0 or 1)
            - name: trx_mode
              description: Identify the mode of the transceiver.
              type: int (0 for estimation mode or 1 for transmission mode)

        responses:
            200:
                description: (int) 0 for OK.
            404:
                description: (int) -1 in case there is some error.

    """
    payload = request.json  # rx_ID, trx_mode values from agent
    try:
        ack = receiver(payload['rx_ID'], payload['trx_mode'])
        return "Oscilloscope ACK {} \n".format(ack)

    except OSError as error:
        return "ERROR: {} \n".format(error)


if __name__ == '__main__':
    # app.run(host='10.1.1.10', port=5000, debug=True)  # REAL
    app.run(host='127.0.0.1', port=5000, debug=True)  # TEST
