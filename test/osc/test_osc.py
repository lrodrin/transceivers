import logging

from os import sys, path

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from lib.osc.osc import OSC

logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    dac_out = 1
    osc_in = 1
    bn = [float(OSC.bps)] * OSC.Ncarriers
    En = [float(1)] * OSC.Ncarriers
    equalization = 0
    rx = OSC()
    result = rx.receiver(dac_out, osc_in, bn, En, equalization)
    print("SNR = {}, BER = {}". format(result[0], result[1]))  # TODO fix
