#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request

from lib.dac.dac import *

METRO_DAC_MATLAB_CALL_WITH_LEIA_DAC_DOWN = '"C:/Program Files/MATLAB/R2010bSP1/bin/matlab.exe" -nodisplay -nosplash ' \
                                           '-nodesktop -r '"Leia_DAC_down; "

METRO_DAC_MATLAB_CALL_WITH_LEIA_DAC_UP = '"C:/Program Files/MATLAB/R2010bSP1/bin/matlab.exe" -nodisplay -nosplash ' \
                                         '-nodesktop -r '"Leia_DAC_up; "

SLEEP_TIME = 100

METRO_DAC_INPUTS_ENABLE_TXT = "Inputs_enable.txt"

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


# DAC bluespace
@app.route('/blue/dac', methods=['POST'])
def blue_dac():
    """
    DAC bluespace route.

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
    payload = request.json  # tx_ID, trx_mode, FEC, bps, pps
    try:
        ack = transmitter(payload['tx_ID'], payload['trx_mode'], payload['FEC'], payload['bps'], payload['pps'])
        return "DAC ACK {}\n".format(ack)

    except OSError as error:
        return "ERROR: {} \n".format(error)


# OSC bluespace
@app.route('/blue/osc', methods=['POST'])
def blue_osc():
    """
    OSC bluespace route.

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
    payload = request.json  # rx_ID, trx_mode, FEC, bps, pps
    try:
        result = receiver(payload['rx_ID'], payload['trx_mode'], payload['FEC'], payload['bps'], payload['pps'])
        return "Oscilloscope ACK {} SNR {} BER {}\n".format(result[0], result[1], result[2])

    except OSError as error:
        return "ERROR: {} \n".format(error)


# DAC metrohaul
@app.route('/metro/dac', methods=['POST'])
def metro_dac():
    """
    DAC metrohaul route.

    post:
        summary: Metrohaul DAC configuration. description: Startup Metrohaul DAC configuration.
        attributes:
            - name: trx_mode
            description: Identify the configuration mode of the transceiver.
            type: int (0 for METRO_1 scenario or 1 for METRO_2 scenario)
            - name: tx_ID
            description: Identify the channel of the DAC to be used and the local files to use for storing data.
            tx_ID when Mode 0 (METRO_1 scenario) is equivalent to select the OpenConfig client. tx_ID when Mode 1
            METRO_2 scenario) is equivalent to select the S_BVT, which includes 2 clients multiplexed in a single
            optical channel. Due to hardware limitations in this last case (METRO2 scenario) tx_ID will be always 0.
            type: int (0 or 1)

        responses:
            200:
                description: (int) 0 for OK.
            404:
                description: (int) -1 in case there is some error.

    """
    payload = request.json  # trx_mode, tx_ID
    scenario = payload['trx_mode']
    channel_id = payload['tx_ID']

    tx = DAC(trx_mode, tx_ID)
    input_file = open(METRO_DAC_INPUTS_ENABLE_TXT, "w")

    if scenario == 0:  # METRO1 scenario with BVTs to demonstrate bidirectionality
        try:
            ack = tx.transmitter()
            if channel_id == 0:
                input_file.write("1\n 0\n 0\n 0\n")  # Hi_en, Hq_en, Vi_en, Vq_en
                os.system(METRO_DAC_MATLAB_CALL_WITH_LEIA_DAC_UP)  # MATLAB call with file Leia_DAC_up.m

            else:
                input_file.write("0\n 1\n 0\n 0\n")  # Hi_en, Hq_en, Vi_en, Vq_en
                os.system(METRO_DAC_MATLAB_CALL_WITH_LEIA_DAC_DOWN)  # MATLAB call with file Leia_DAC_down.m

            time.sleep(SLEEP_TIME)
            print('Leia initialized and SPI input_file uploaded')
            return "DAC ACK {}\n".format(ack)

        except OSError as error:
            return "ERROR: {} \n".format(error)


    elif scenario == 1:  # METRO2 scenario with an SBVT. In this case tx_ID can not be modified as the two slices are
        # multiplexed in a superchannel and are created in the same function call
        try:
            if channel_id == 0:
                ack = tx.transmitter()
                input_file.write("1\n 0\n 0\n 0\n")  # Hi_en, Hq_en, Vi_en, Vq_en
                os.system(METRO_DAC_MATLAB_CALL_WITH_LEIA_DAC_UP)  # MATLAB call with file Leia_DAC_up.m
                time.sleep(SLEEP_TIME)
                print('Leia initialized and SPI input_file uploaded')
                return "DAC ACK {}\n".format(ack)

            if channel_id == 1:
                ack = tx.transmitter()
                input_file.write("0\n 1\n 0\n 0\n")  # Hi_en, Hq_en, Vi_en, Vq_en
                os.system(METRO_DAC_MATLAB_CALL_WITH_LEIA_DAC_DOWN)  # MATLAB call with file Leia_DAC_down.m
                time.sleep(SLEEP_TIME)
                print('Leia initialized and SPI input_file uploaded')
                return "DAC ACK {}\n".format(ack)

        except OSError as error:
            return "ERROR: {} \n".format(error)


# OSC metrohaul
@app.route('/metro/osc', methods=['POST'])
def metro_osc():
    """
    OSC metrohaul route.

    post:
        summary: Metrohaul DAC configuration.
        description: Startup Metrohaul OSC configuration.
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
    payload = request.json  # rx_ID, trx_mode
    try:
        ack = receiver(payload['rx_ID'], payload['trx_mode'])
        return "Oscilloscope ACK {} \n".format(ack)

    except OSError as error:
        return "ERROR: {} \n".format(error)


if __name__ == '__main__':
    # app.run(host='10.1.1.10', port=5000, debug=True) # REAL
    app.run(host='127.0.0.1', port=5000, debug=True)  # TEST
