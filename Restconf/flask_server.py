#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request

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
        summary: Metrohaul DAC configuration.
        description: Startup Metrohaul DAC configuration.
        attributes:
            - name: trx_mode
              description: Identify the configuration mode of the transceiver.
              type: int (0 for configuration 1 mode or 1 for configuration 2 mode)
            - name: tx_ID
              description: Identify the channel of the DAC to be used and the local files to use for storing data.
              type: int (0 or 1)

        responses:
            200:
                description: (int) 0 for OK.
            404:
                description: (int) -1 in case there is some error.

    """
    payload = request.json  # trx_mode, tx_ID
    scenario = payload['trx_mode']
    if scenario == 0:
        try:
            ack = transmitter(scenario, payload['tx_ID'])
            return "DAC ACK {}\n".format(ack)

        except OSError as error:
            return "ERROR: {} \n".format(error)

    elif scenario == 1:
        try:
            ack = transmitter(scenario, payload['tx_ID'])
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
