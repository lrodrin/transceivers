from os import sys, path

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from lib.osc.osc import OSC

if __name__ == '__main__':
    trx_mode = 0
    rx_ID = 1
    rx = OSC(trx_mode, rx_ID, None, 2, None)
    ack = rx.receiver()
    print('ACK = ', ack)
