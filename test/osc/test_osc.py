import logging

from os import sys, path

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from lib.osc.osc import OSC

logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    ip_server = '10.1.7.64'
    params = {'tx_mode': 0, 'rx_ID': 0, 'bn': 2, 'En': 0, 'eq': 0}
    rx = OSC()
    snr, ber = rx.receiver(params['tx_mode'], params['rx_ID'], params['bn'], params['En'], params['eq'])
    print(snr, ber)
