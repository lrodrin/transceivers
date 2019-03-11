import logging
import operator
from collections import Counter
from os import sys, path

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from lib.wss.wss import WSS

logging.basicConfig(level=logging.DEBUG)


def n_max(operations, key_func):
    """
    Return the maximum element of input ports into operations.

    :param operations: operations to configure the WaveShaper
    :type operations: list
    :param key_func: comparison key
    :type key_func: str
    :return: maximum element of input ports
    :rtype: int
    """
    maximum = 0
    for i in range(len(operations)):
        if operations[i][key_func] > maximum:
            maximum = operations[i][key_func]
    return maximum


if __name__ == '__main__':
    params_wss1 = [{'port_in': 1, 'port_out': 1, 'lambda0': 1550.52, 'att': 0.0, 'phase': 0.0, 'bw': 112.5}]

    params_wss2 = [{'port_in': 2, 'port_out': 1, 'lambda0': 1550.88, 'att': 0.0, 'phase': 0.0, 'bw': 50.0},
                   {'port_in': 3, 'port_out': 1, 'lambda0': 1550.3, 'att': 0.0, 'phase': 0.0, 'bw': 50.0}]

    # WSS1
    wss_id = 1
    logging.debug("WaveShaper %s configuration started" % wss_id)
    n = n_max(params_wss1, 'port_in')
    m = 1
    print(n, m)
    wss = WSS(wss_id, n, m)
    wss.configuration(params_wss1)
    logging.debug("WaveShaper %s configuration finished" % wss_id)

    # WSS2
    wss_id = 2
    logging.debug("WaveShaper %s configuration started" % wss_id)
    n = n_max(params_wss2, 'port_in')
    m = 1
    print(n, m)
    wss = WSS(wss_id, n, m)
    wss.configuration(params_wss2)
    print(wss.wavelength)
    logging.debug("WaveShaper %s configuration finished" % wss_id)
