from flask import Flask

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


if __name__ == '__main__':
    # app.run(host='10.1.1.10', port=5000, debug=True) # REAL
    app.run(host='10.1.16.53', port=5000, debug=True)  # TEST
