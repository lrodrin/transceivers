import logging

from os import sys, path

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from lib.dac.dac import DAC

logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    params = {'tx_ID': 0, 'bn': 2, 'En': 0}
    tx = DAC()
    tx.transmitter(params['tx_ID'], params['bn'], params['En'])
