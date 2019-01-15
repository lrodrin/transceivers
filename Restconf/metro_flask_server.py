#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/api/vi/openconfig/local_assignment', methods=['POST'])
def local_assignment():
    """
    ? route.

    post:
        summary: C1 over Ochα or Ochβ (C1 -> Ochα)
        description: ?
        attributes:
            - name: client
              description: Identify the client to be used.
              type: string (C1 or C2)
            - name: Ochα
              description: ?
              type: string

        responses:
            200:
                description: (string) Ok.
            404:
                description: (string) no_ok in case there is some error.

    """
    payload = request.json  # client, Ochα from client
    try:
        ack = python_xc(payload['client'], payload['Ochα'])
        return "ACK {}\n".format(ack)

    except OSError as error:
        return "ERROR: {} \n".format(error)


@app.route('/api/vi/openconfig/optical_channel', methods=['POST'])
def optical_channel_configuration():
    """
    Optical Channel Configuration route.

    post:
        summary: Configuration of the terminal optical channel (Och).
        description: Configure Ochα or Ochβ by setting frequency, power and mode of the optical channel.
        attributes:
            - name: Ochα
              description: ?
              type: string
            - name: freq
              description: Frequency of the optical channel, expressed in MHz.
              type: int
            - name: pow
              description: Power of the optical channel, expressed in increments of 0.01 dBm.
              type: int
            - name: frew
              description: Frequency of the optical channel, expressed in MHz.
              type: int

        responses:
            200:
                description: (string) Ok.
            404:
                description: (string) no_ok in case there is some error.

    """
    payload = request.json  # Ochα, freq, pow and mode from client
    try:
        ack = python_f(payload['Ochα'], payload['freq'], payload['pow'], payload['mode'])
        # laser
        # amplis
        # dac
        # osc
        return "ACK {}\n".format(ack)

    except OSError as error:
        return "ERROR: {} \n".format(error)


if __name__ == '__main__':
    # app.run(host='10.1.1.10', port=5000, debug=True) # REAL
    app.run(host='127.0.0.1', port=5000, debug=True)  # TEST
