import subprocess
import time

from flask import Flask, request

from lib.amp import Amp
from lib.laser import Laser

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

app = Flask('server')


# DAC
@app.route('/api/dac', methods=['POST'])
def startup_dac():
    process_name = request.args.keys()
    try:
        subprocess.call(process_name[0])
        return "Called: {} \n".format(process_name)

    except OSError as error:
        return "ERROR: {} \n".format(error)


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
