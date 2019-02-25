import logging
from collections import Counter
from os import sys, path

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

logging.basicConfig(level=logging.DEBUG)

from lib.wss.wss import WSS


def calculateNxM(operations):
    """
    Calculate the total number of input and output ports of an operation.

    :param operations: operations that configure a WaveShaper
    :type operations: list
    :return: number of input (n) and output ports (m)
    :rtype: int, int
    """
    n = Counter()
    m = Counter()
    for op in operations:
        n[op["port_in"]] += 1
        m[op["port_out"]] += 1

    return len(n), len(m)


if __name__ == '__main__':
    wss_id = 1  # 1 or 2
    if wss_id == 1:
        params = [{'port_in': 1, 'port_out': 1, 'lambda0': 1550.99, 'att': 0.0, 'phase': 0.0, 'bw': 25}]

    else:
        params = [{'port_in': 1, 'port_out': 1, 'lambda0': 1550.99, 'att': 0.0, 'phase': 0.0, 'bw': 25}]
        # params = [{'port_in': 1, 'port_out': 1, 'lambda0': 1550.99, 'att': 0.0, 'phase': 0.0, 'bw': 25},
        #           {'port_in': 2, 'port_out': 1, 'lambda0': 1550.12, 'att': 0.0, 'phase': 0.0, 'bw': 25},
        #           {'port_in': 3, 'port_out': 1, 'lambda0': 1549.3, 'att': 0.0, 'phase': 0.0, 'bw': 25},
        #           {'port_in': 4, 'port_out': 1, 'lambda0': 1548.5, 'att': 0.0, 'phase': 0.0, 'bw': 25}]

    n, m = calculateNxM(params)
    wss_tx = WSS(wss_id, n, m)
    wss_tx.configuration(params)
