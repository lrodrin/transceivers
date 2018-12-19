import time

from flask import Flask, request

from lib.amp import Amp
from lib.laser import Laser

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

app = Flask('server')


# DAC bluespace
@app.route('/api/blue/dac', methods=['POST'])
def startup_dac():
    payload = request.json  # tx_ID, trx_mode, FEC, bps, pps
    try:
        ack = transmitter(payload['tx_ID'], payload['trx_mode'], payload['FEC'], payload['bps'], payload['pps'])
        return "DAC ACK {}\n".format(ack)

    except OSError as error:
        return "ERROR: {} \n".format(error)


# OSC bluespace
@app.route('/api/blue/osc', methods=['POST'])
def startup_osc():
    payload = request.json  # rx_ID, trx_mode, FEC, bps, pps
    try:
        result = receiver(payload['rx_ID'], payload['trx_mode'], payload['FEC'], payload['bps'], payload['pps'])
        return "Oscilloscope ACK {} SNR {} BER {}\n".format(result[0], result[1], result[2])

    except OSError as error:
        return "ERROR: {} \n".format(error)


# DAC metrohaul
@app.route('/api/metro/dac', methods=['POST'])
def startup_dac():
    payload = request.json  # scenario, tx_ID
    scenario = payload['scenario']
    if scenario == "METRO_1":
        try:
            pass
            # python_xc(1, 1) # client opticalchannel
            # python_f(1, 193400000, 14, 2) # opticalchannel frequency power trx_mode
            # ?
            # python_disconnect()

        except OSError as error:
            return "ERROR: {} \n".format(error)

    elif scenario == "METRO_2":
        try:
            pass

        except OSError as error:
            return "ERROR: {} \n".format(error)


# OSC metrohaul
@app.route('/api/metro/osc', methods=['POST'])
# def startup_osc():
#     payload = request.json  # rx_ID
#     try:
#         ack = receiver(payload['rx_ID'])
#         return "Oscilloscope ACK {}\n".format(ack)
#
#     except OSError as error:
#         return "ERROR: {} \n".format(error)

# TODO merge DAC bluespace with metrohaul
# TODO merge OSC bluespace with metrohaul

# Laser
@app.route('/api/laser', methods=['POST'])
def startup_laser():
    payload = request.json  # channel, wavelength, power, status
    yenista = Laser()
    try:
        channel = payload['channel']
        yenista.wavelength(channel, payload['wavelength'])  # define wavelength
        yenista.power(channel, payload['power'])  # define power
        yenista.enable(channel, payload['status'])  # enable laser
        time.sleep(10)
        result = yenista.status(channel)  # check status, wavelength, power
        print(yenista.test())
        yenista.close()
        return "Laser status {}  wavelength {} power {}\n".format(result[0], result[1], result[2])

    except OSError as error:
        return "ERROR: {} \n".format(error)


# Amplifier
@app.route('/api/amp', methods=['POST'])
def startup_amp():
    payload = request.json  # ip, mode, power, status
    manlight = Amp(payload['ip'])
    try:
        print(manlight.test())
        manlight.mode(payload['mode'], payload['power'])  # define mode
        manlight.enable(payload['status'])  # enable EDFA
        result = manlight.status()  # check status, mode, power
        manlight.close()
        return "Amplifier status {}  mode {} power {}\n".format(result[0], result[1], result[2])

    except OSError as error:
        return "ERROR: {} \n".format(error)


if __name__ == '__main__':
    app.run(host='10.1.1.10', port=5000, debug=True)
