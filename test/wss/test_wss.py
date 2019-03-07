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
    n = Counter()
    m = Counter()
    for op in operation:
        n[op["port_in"]] += 1
        m[op["port_out"]] += 1

    return len(n), len(m)


if __name__ == '__main__':
    params_wss1 = [{'port_in': 1, 'port_out': 1, 'lambda0': 1550.12, 'att': 0.0, 'phase': 0.0, 'bw': 25}]

    params_wss2 = [{'port_in': 1, 'port_out': 1, 'lambda0': 1550.92, 'att': 0.0, 'phase': 0.0, 'bw': 25},
    {'port_in': 2, 'port_out': 1, 'lambda0': 1550.12, 'att': 0.0, 'phase': 0.0, 'bw': 25}]
    # params_wss2 = [{'port_in': 1, 'port_out': 1, 'lambda0': 1550.99, 'att': 0.0, 'phase': 0.0, 'bw': 25},
    #           {'port_in': 2, 'port_out': 1, 'lambda0': 1550.12, 'att': 0.0, 'phase': 0.0, 'bw': 25},
    #           {'port_in': 3, 'port_out': 1, 'lambda0': 1549.3, 'att': 0.0, 'phase': 0.0, 'bw': 25},
    #           {'port_in': 4, 'port_out': 1, 'lambda0': 1548.5, 'att': 0.0, 'phase': 0.0, 'bw': 25}]

    # WSS1
    wss_id = 1
    logging.debug("WaveShaper %s configuration started" % wss_id)
    n, m = calculateNxM(params_wss1)
    print(n, m)
    # wss = WSS(wss_id, n, m)
    # wss.configuration(params_wss1)
    # logging.debug("WaveShaper %s configuration finished" % wss_id)

    # WSS2
    wss_id = 2
    logging.debug("WaveShaper %s configuration started" % wss_id)
    n, m = calculateNxM(params_wss2)
    print(n, m)
    #wss = WSS(wss_id, n, m)
    #wss.configuration(params_wss2)
    #logging.debug("WaveShaper %s configuration finished" % wss_id)
