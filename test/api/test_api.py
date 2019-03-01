import logging
from os import sys, path

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from lib.dac.dac import DAC
from rest_api import RestApi

logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    params_wss_1 = {'wss_id': 1, 'operation': [
        {'port_in': 1, 'port_out': 1, 'lambda0': 1550.99, 'att': 0.0, 'phase': 0.0, 'bw': 25}]}
    params_wss_2 = {'wss_id': 2, 'operation': [
        {'port_in': 1, 'port_out': 1, 'lambda0': 1550.99, 'att': 0.0, 'phase': 0.0, 'bw': 25}]}

    bn = [float(DAC.bps)] * DAC.Ncarriers
    En = [float(1)] * DAC.Ncarriers
    params_dac_osc = [{'id': 1, 'dac_out': 1, 'osc_in': 1, 'bn': bn, 'En': En, 'eq': 0},
                      {'id': 2, 'dac_out': 2, 'osc_in': 2, 'bn': bn, 'En': En, 'eq': 0}]

    api = RestApi('10.1.1.10')
    # WSS
    print(api.WSSConfiguration(params_wss_1))
    print(api.WSSConfiguration(params_wss_2))
    print(api.getWSSOperationsById(1))
    print(api.getWSSOperationsById(2))
    print(api.deleteWSSOperationsById(1))
    print(api.getWSSOperations())

    # DAC/OSC
    print(api.DACOSCConfiguration(params_dac_osc))
    print(api.getDACOSCOperationsById(1))
    print(api.getDACOSCOperationsById(2))
    print(api.deleteDACOSCOperationsById(1))
    print(api.getDACOSCOperations())
