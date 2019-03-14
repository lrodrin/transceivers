import logging
import numpy as np
from os import sys, path

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from lib.dac.dac import DAC
from rest_api import RestApi

logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    wss1 = {'wss_id': 1, 'operations': [
        {'port_in': 1, 'port_out': 1, 'lambda0': 1550.52, 'att': 0.0, 'phase': 0.0, 'bw': 112.5}]}

    wss2 = {'wss_id': 2, 'operations': [
        {'port_in': 2, 'port_out': 1, 'lambda0': 1550.88, 'att': 0.0, 'phase': 0.0, 'bw': 50.0},
        {'port_in': 3, 'port_out': 1, 'lambda0': 1550.3, 'att': 0.0, 'phase': 0.0, 'bw': 50.0}]}

    bn1 = np.array(np.ones(DAC.Ncarriers) * DAC.bps).tolist()
    bn2 = np.array(np.ones(DAC.Ncarriers) * DAC.bps).tolist()
    En1 = np.array(np.ones(DAC.Ncarriers)).tolist()
    En2 = np.round(np.array(np.ones(DAC.Ncarriers) / np.sqrt(2)), 3).tolist()
    eq1 = eq2 = "MMSE"
    params = [{'id': 1, 'dac_out': 1, 'osc_in': 2, 'bn': bn1, 'En': En1, 'eq': eq1},
              {'id': 2, 'dac_out': 2, 'osc_in': 1, 'bn': bn2, 'En': En2, 'eq': eq2}]

    logging.debug("Testing REST API")
    api = RestApi('10.1.1.10')

    # WSS
    logging.debug("WSS")
    print(api.wSSConfiguration(wss1))
    print(api.wSSConfiguration(wss2))
    print(api.getWSSOperations())
    print(api.getWSSOperationsById(1))
    print(api.getWSSOperationsById(2))
    print(api.deleteWSSOperationsById(2))
    print(api.getWSSOperations())

    # DAC/OSC
    logging.debug("DAC and OSC")
    print(api.dacOscConfiguration(params))
    print(api.getDACOSCOperations())
    print(api.getDACOSCOperationsById(1))
    print(api.getDACOSCOperationsById(2))
    print(api.deleteDACOSCOperationsById(1))
    print(api.getDACOSCOperations())
