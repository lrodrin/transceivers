import time

from flask import Flask, request
from os import sys, path

TIME_SLEEP = 5
AMPLIFIER_ADDR = '3'
IP_AMPLIFIER_2 = '10.1.1.16'
IP_AMPLIFIER_1 = '10.1.1.15'
IP_LASER = '10.1.1.7'
LASER_ADDR = '11'
SPEED_OF_LIGHT = 299792458

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from lib.laser.laser import Laser
from lib.amp.amp import Amplifier

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

app = Flask(__name__)


@app.route('/api/hello', methods=['GET'])
def hello_world():  # TODO esborrar quan fucnioni tot
    return 'Hello, World!'


def python_xc(cl, och):
    """
    Show the client assigned to the optical channel.

    :param cl: client
    :param och: optical channel assigned
    :type cl: str
    :type och: str
    """
    print("Client " + cl + " assigned to optical channel " + och)


@app.route('/api/vi/openconfig/local_assignment', methods=['POST'])
def local_assignment():
    """
    ? route.

    post:
    summary: ?.
    description: Reference to the line-side optical channel that should carry the current logical
    channel element. Use this reference to exit the logical element stage.
    attributes:
        - name: client
          description: Identify the client to be used.
          type: string (C1 or C2)
        - name: Och
          description: Identify the optical channel to be used.
          type: string

        responses:
            200:
                description: (string) OK.
            404:
                description: (string) no_ok in case there is some error.

    """
    payload = request.json  # client, Och from agent
    try:
        python_xc(payload['client'], payload['Och'])
        return "OK\n"

    except OSError as error:
        return "no_ok: {} \n".format(error)


def python_f(och, freq, powL, modeA, modeB, powA, powB):
    """
    Terminal Optical Channel Configuration.
        - Laser configuration
        - Amplifiers configuration.
        - Waveshaper configuration.
        - DAC configuration.
        - OSC configuration.

    :param och: optical channel
    :param freq: frequency of the laser
    :param powL: power of the laser
    :param modeA: mode of the amplifiers one
    :param modeB: mode of the amplifiers two
    :param powA_1: power of amplifier one
    :param powA_2: power of amplifier two
    """
    # Laser configuration
    laser_configuration(freq, och, powL)
    manlight_1 = Amplifier(IP_AMPLIFIER_1, AMPLIFIER_ADDR)
    manlight_2 = Amplifier(IP_AMPLIFIER_2, AMPLIFIER_ADDR)
    manlight_1.mode(modeA, powA)
    manlight_2.mode(modeB, powB)
    manlight_1.enable(True)
    manlight_2.enable(True)
    time.sleep(TIME_SLEEP)
    print(manlight_1.status())
    print(manlight_2.status())
    print(manlight_1.test())
    print(manlight_2.test())
    manlight_1.close()
    manlight_2.close()


def laser_configuration(freq, och, pow):
    """
    Laser Configuration.

    :param freq: frequency
    :param och: optical channel
    :param pow: power
    :type freq: int
    :type och: int
    :type pow: float
    """
    yenista = Laser(IP_LASER, LASER_ADDR)
    print(yenista.test())
    yenista.enable(och, True)  # Switch on channel och of the laser
    # c = 3e8 # Speed of light in m/s
    lambda0 = (SPEED_OF_LIGHT / (freq * 1e6)) * 1e9  # Wavelength in nm
    yenista.wavelength(och, lambda0)
    yenista.power(och, pow)
    # if we use an OA in the setup after the MZM pow= pow+G, where G is the gain of the OA in dB
    time.sleep(TIME_SLEEP)
    print(yenista.status(och))
    yenista.close()


@app.route('/api/vi/openconfig/optical_channel', methods=['POST'])
def optical_channel_configuration():
    """
    Optical Channel Configuration route.

    post:
        summary: Configuration of the terminal optical channel (Och).
        description: Configure the optical channel Och by setting frequency, power and mode of the optical channel.
        attributes:
            - name: Och
              description: Optical channel.
              type: string
            - name: freq
              description: Frequency of the optical channel, expressed in MHz.
              type: int
            - name: pow
              description: Power of the optical channel, expressed in increments of 0.01 dBm.
              type: int
            - name: mode
              description: Vendor-specific mode identifier -- sets the operational mode for the channel. The specified
              operational mode must exist in the list of supported operational modes supplied by the device.
              type: int

        responses:
            200:
                description: (string) OK.
            404:
                description: (string) no_ok in case there is some error.

    """
    payload = request.json  # Och, freq, pow and mode from agent
    try:
        python_f(payload['Och'], payload['freq'], payload['pow'], payload['mode'])
        return "OK\n"

    except OSError as error:
        return "no_ok: {} \n".format(error)


if __name__ == '__main__':
    # app.run(host='10.1.7.65', port=5000, debug=True)  # REAL
    app.run(host='127.0.0.1', port=5000, debug=True)  # TEST
