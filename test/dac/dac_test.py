from os import sys, path

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from lib.dac.dac import DAC


if __name__ == '__main__':
    trx_mode = 0
    tx_ID = 0
    tx = DAC(trx_mode, tx_ID, None, 2, None)
    ack = tx.transmitter()
    print('ACK = ', ack)


