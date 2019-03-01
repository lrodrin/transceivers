import logging
from collections import Counter
from os import sys, path

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from lib.wss.wss import WSS

logging.basicConfig(level=logging.DEBUG)


def calculateNxM(operation):
    """
    Calculate the total number of input and output ports of an operation.

    :param operation: operations that configure a WaveShaper
    :type operation: list
    :return: number of input (n) and output ports (m)
    :rtype: int, int
    """
    n = m = Counter()
    for op in operation:
        n[op["port_in"]] += 1
        m[op["port_out"]] += 1

    return len(n), len(m)


if __name__ == '__main__':
    params_wss1 = [{'port_in': 1, 'port_out': 1, 'lambda0': 1550.99, 'att': 0.0, 'phase': 0.0, 'bw': 25}]

    params_wss2 = [{'port_in': 1, 'port_out': 1, 'lambda0': 1550.99, 'att': 0.0, 'phase': 0.0, 'bw': 25}]
    # params_wss2 = [{'port_in': 1, 'port_out': 1, 'lambda0': 1550.99, 'att': 0.0, 'phase': 0.0, 'bw': 25},
    #           {'port_in': 2, 'port_out': 1, 'lambda0': 1550.12, 'att': 0.0, 'phase': 0.0, 'bw': 25},
    #           {'port_in': 3, 'port_out': 1, 'lambda0': 1549.3, 'att': 0.0, 'phase': 0.0, 'bw': 25},
    #           {'port_in': 4, 'port_out': 1, 'lambda0': 1548.5, 'att': 0.0, 'phase': 0.0, 'bw': 25}]

    # WSS1
    n, m = calculateNxM(params_wss1)
    wss = WSS(1, n, m)
    wss.configuration(params_wss1)

    # WSS2
    n, m = calculateNxM(params_wss2)
    wss = WSS(2, n, m)
    wss.configuration(params_wss2)
