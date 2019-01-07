import time

from flask import Flask, request
from lib.amp import Amp
from lib.laser import Laser

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


# DAC bluespace
# @app.route('/blue/dac', methods=['POST'])
# def dac():
#     payload = request.json  # tx_ID, trx_mode, FEC, bps, pps
#     try:
#         ack = transmitter(payload['tx_ID'], payload['trx_mode'], payload['FEC'], payload['bps'], payload['pps'])
#         return "DAC ACK {}\n".format(ack)
#
#     except OSError as error:
#         return "ERROR: {} \n".format(error)
#
#
# # OSC bluespace
# @app.route('/blue/osc', methods=['POST'])
# def osc():
#     payload = request.json  # rx_ID, trx_mode, FEC, bps, pps
#     try:
#         result = receiver(payload['rx_ID'], payload['trx_mode'], payload['FEC'], payload['bps'], payload['pps'])
#         return "Oscilloscope ACK {} SNR {} BER {}\n".format(result[0], result[1], result[2])
#
#     except OSError as error:
#         return "ERROR: {} \n".format(error)
#
#
# # DAC metrohaul
# @app.route('/metro/dac', methods=['POST'])
# def dac():
#     payload = request.json  # trx_mode, tx_ID
#     scenario = payload['trx_mode']
#     if scenario == "METRO_1":
#         try:
#             ack = transmitter(scenario, payload['tx_ID'])
#             return "DAC ACK {}\n".format(ack)
#
#         except OSError as error:
#             return "ERROR: {} \n".format(error)
#
#     elif scenario == "METRO_2":
#         try:
#             pass
#
#         except OSError as error:
#             return "ERROR: {} \n".format(error)
#
#
# # OSC metrohaul
# @app.route('/metro/osc', methods=['POST'])
# def osc():
#     payload = request.json  # rx_ID, trx_mode
#     try:
#         ack = receiver(payload['rx_ID'], payload['trx_mode'])
#         return "Oscilloscope ACK {} \n".format(ack)
#
#     except OSError as error:
#         return "ERROR: {} \n".format(error)
#


@app.route('/laser', methods=['POST'])
def laser():
    """
    Laser route.

    post:
        summary: Laser configuration.
        description: Modify a laser configuration.
        parameters:
        responses:
            200:
                description: Laser status, wavelength and power to be returned.
            404:
                description: Laser not operative.

    """
    payload = request.json  # channel, wavelength, power, status
    yenista = Laser()
    try:
        print(yenista.test())
        channel = payload['channel']
        yenista.wavelength(channel, payload['wavelength'])  # define wavelength
        yenista.power(channel, payload['power'])  # define power
        yenista.enable(channel, payload['status'])  # enable laser
        time.sleep(5)
        result = yenista.status(channel)  # check status, wavelength, power
        yenista.close()
        return "Laser status {}, wavelength {}, power {}\n".format(result[0], result[1], result[2])

    except OSError as error:
        return "ERROR: {} \n".format(error)


@app.route('/amp', methods=['POST'])
def amp():
    """
    Amplifier route.

    post:
        summary: Amplifier configuration.
        description: Modify an amplifier configuration.
        parameters:
        responses:
            200:
                description: Amplifier status, mode and power to be returned.
            404:
                description: Amplifier not operative.

    """
    payload = request.json  # ip, mode, power, status
    manlight = Amp(payload['ip'])
    try:
        print(manlight.test())
        manlight.mode(payload['mode'], payload['power'])  # define mode
        manlight.enable(payload['status'])  # enable EDFA
        time.sleep(5)
        result = manlight.status()  # check status, mode, power
        manlight.close()
        return "Amplifier status {}, mode {}, power {}\n".format(result[0], result[1], result[2])

    except OSError as error:
        return "ERROR: {} \n".format(error)


if __name__ == '__main__':
    # app.run(host='10.1.1.10', port=5000, debug=True) # REAL
    app.run(host='10.1.16.53', port=5000, debug=True)  # TEST
