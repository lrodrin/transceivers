import logging

from os import sys, path

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from lib.dac.dac import DAC

logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    dac_out = 1
    bn = [float(DAC.bps)] * DAC.Ncarriers
    En = [float(1)] * DAC.Ncarriers
    tx = DAC()
    tx.transmitter(dac_out, bn, En)  # TODO fix
