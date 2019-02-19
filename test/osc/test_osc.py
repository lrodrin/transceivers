import logging

from os import sys, path

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from lib.osc.osc import OSC

logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    tx_mode = 0
    rx_ID = 0
    bn = [float(OSC.bps)] * OSC.Ncarriers
    En = [float(1)] * OSC.Ncarriers
    equalization = 0
    rx = OSC()
    params = rx.receiver(tx_mode, rx_ID, bn, En, equalization)
    print("SNR = {}, BER = {}". format(params[0], params[1]))  # TODO fix
