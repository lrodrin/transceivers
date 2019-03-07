import logging
import numpy as np
from os import sys, path

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from lib.dac.dac import DAC
from rest_api import RestApi

logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    params_wss_1 = {'wss_id': 1, 'operation': [
        {'port_in': 1, 'port_out': 1, 'lambda0': 1550.52, 'att': 0.0, 'phase': 0.0, 'bw': 112.5}]}

    params_wss_2 = {'wss_id': 2, 'operation': [
        {'port_in': 1, 'port_out': 1, 'lambda0': 1550.52, 'att': 0.0, 'phase': 0.0, 'bw': 112.5},
        {'port_in': 2, 'port_out': 1, 'lambda0': 1550.12, 'att': 0.0, 'phase': 0.0, 'bw': 25}]}

    bn1 = [float(2)] * DAC.Ncarriers
    bn2 = [float(1)] * DAC.Ncarriers
    En1 = [float(1)] * DAC.Ncarriers
    En2 = ([round(float(1 / np.sqrt(2)), 3)] * DAC.Ncarriers)
    eq1 = eq2 = "MMSE"
    params_dac_osc = [{'id': 1, 'dac_out': 1, 'osc_in': 2, 'bn': bn1, 'En': En1, 'eq': eq1},
              {'id': 2, 'dac_out': 2, 'osc_in': 1, 'bn': bn2, 'En': En2, 'eq': eq2}]

    api = RestApi('10.1.1.10')
    logging.debug("Testing REST API")
    # WSS
    logging.debug("WSS")
    print(api.WSSConfiguration(params_wss_1))
    print(api.WSSConfiguration(params_wss_2))
    print(api.getWSSOperations())
    print(api.getWSSOperationsById(1))
    print(api.getWSSOperationsById(2))
    print(api.deleteWSSOperationsById(2))
    print(api.getWSSOperations())

    # DAC/OSC
    logging.debug("DAC and OSC")
    print(api.DACOSCConfiguration(params_dac_osc))
    print(api.getDACOSCOperationsById(1))
    print(api.getDACOSCOperationsById(2))
    print(api.deleteDACOSCOperationsById(1))
    print(api.getDACOSCOperations())
