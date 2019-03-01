"""This is the REST API module.
"""
import json
import logging
import requests

from os import sys, path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from lib.dac.dac import DAC

logging.basicConfig(level=logging.DEBUG)  # TODO change logging to logger

HEADERS = {"Content-Type": "application/json"}


class RestApi:
    """
    This is a class for the REST API module.

    :ivar int port_dac_osc: number of DAC/OSC REST Server port
    :ivar int port_wss: number of WSS REST Server port
    """

    def __init__(self, ip):
        """
        The constructor for the REST API class.

        :param ip: ip address
        :type ip: str
        """
        self.ip = ip
        self.port_dac_osc = 5000
        self.port_wss = 5001

    def DACOSCConfiguration(self, params):
        """
        DAC and OSC configuration.

        :param params: # TODO
        :type params: list
        :return:    # TODO
        :rtype: dict
        """
        logging.debug('RestApi.DACOSCConfiguration')
        url = "http://" + self.ip + ':' + str(self.port_dac_osc) + "/api/dac_osc"
        try:
            response = requests.post(url, headers=HEADERS, data=json.dumps(params))
            logging.debug('Response from {}:\n\t{}'.format(url, response.content))
            data = response.content

        except Exception as e:
            logging.error(e)
            raise e

        return data

    def WSSConfiguration(self, params):
        """
        WaveShaper configuration.

        :param params: id and a set of operations to configure the WaveShaper
        :type params: dict
        :return:    # TODO
        :rtype: dict
        """
        logging.debug('RestApi.WSSConfiguration')
        url = "http://" + self.ip + ':' + str(self.port_wss) + "/api/wss"
        try:
            response = requests.post(url, headers=HEADERS, data=json.dumps(params))
            logging.debug('Response from {}:\n\t{}'.format(url, response.content))
            data = response.content

        except Exception as e:
            logging.error(e)
            raise e

        return data

    def getDACOSCOperations(self):
        """
        Get all the logical associations between DAC and OSC.

        :return: # TODO
        :rtype: dict
        """
        logging.debug('RestApi.getDACOSCOperations')
        url = "http://" + self.ip + ':' + str(self.port_dac_osc) + "/api/dac_osc"
        print(url)
        try:
            response = requests.get(url, headers=HEADERS)
            logging.debug('Response from {}:\n\t{}'.format(url, response.content))
            data = response.content

        except Exception as e:
            logging.error(e)
            raise e

        return data

    def getWSSOperations(self):
        """
        Get all the operations from a set of WaveShaper.

        :return: # TODO
        :rtype: dict
        """
        logging.debug('RestApi.getWSSOperations')
        url = "http://" + self.ip + ':' + str(self.port_wss) + "/api/wss"
        print(url)
        try:
            response = requests.get(url, headers=HEADERS)
            logging.debug('Response from {}:\n\t{}'.format(url, response.content))
            data = response.content

        except Exception as e:
            logging.error(e)
            raise e

        return data

    def getDACOSCOperationsById(self, assoc_id):
        """
         Get all the logical associations between DAC and OSC specified by id.

        :param assoc_id: logical association id
        :type assoc_id: int
        :return: # TODO
        :rtype: dict
        """
        logging.debug('RestApi.getDACOSCOperationsById')
        url = "http://" + self.ip + ':' + str(self.port_dac_osc) + "/api/dac_osc/" + str(assoc_id)
        print(url)
        try:
            response = requests.get(url, headers=HEADERS)
            logging.debug('Response from {}:\n\t{}'.format(url, response.content))
            data = response.content

        except Exception as e:
            logging.error(e)
            raise e

        return data

    def getWSSOperationsById(self, wss_id):
        """
        Get the operations from a WaveShaper specified by id.

        :param wss_id: WaveShaper id
        :type wss_id: int
        :return: # TODO
        :rtype: dict
        """
        logging.debug('RestApi.getWSSOperationsById')
        url = "http://" + self.ip + ':' + str(self.port_wss) + "/api/wss/" + str(wss_id)
        print(url)
        try:
            response = requests.get(url, headers=HEADERS)
            logging.debug('Response from {}:\n\t{}'.format(url, response.content))
            data = response.content

        except Exception as e:
            logging.error(e)
            raise e

        return data

    def deleteDACOSCOperationsById(self, assoc_id):
        """
        Delete all the logical associations between DAC and OSC specified by id.

        :param assoc_id: logical association id
        :type assoc_id: int
        :return: # TODO
        :rtype: dict
        """
        logging.debug('RestApi.deleteDACOSCOperationsById')
        url = "http://" + self.ip + ':' + str(self.port_dac_osc) + "/api/dac_osc/" + str(assoc_id)
        print(url)
        try:
            response = requests.delete(url, headers=HEADERS)
            logging.debug('Response from {}:\n\t{}'.format(url, response.content))
            data = response.content

        except Exception as e:
            logging.error(e)
            raise e

        return data

    def deleteWSSOperationsById(self, wss_id):
        """
        Delete operations from a WaveShaper specified by id.

        :param wss_id: WaveShaper id
        :type wss_id: int
        :return: # TODO
        :rtype: dict
        """
        logging.debug('RestApi.deleteWSSOperationsById')
        url = "http://" + self.ip + ':' + str(self.port_wss) + "/api/wss/" + str(wss_id)
        print(url)
        try:
            response = requests.delete(url, headers=HEADERS)
            logging.debug('Response from {}:\n\t{}'.format(url, response.content))
            data = response.content

        except Exception as e:
            logging.error(e)
            raise e

        return data


if __name__ == '__main__':
    print("Testing REST API")
    params_wss_1 = {'wss_id': 1, 'operation': [
        {'port_in': 1, 'port_out': 1, 'lambda0': 1550.99, 'att': 0.0, 'phase': 0.0, 'bw': 25}]}
    params_wss_2 = {'wss_id': 2, 'operation': [
        {'port_in': 1, 'port_out': 1, 'lambda0': 1550.99, 'att': 0.0, 'phase': 0.0, 'bw': 25}]}

    api = RestApi('10.1.1.10')
    # print(api.WSSConfiguration(params_wss_1))
    # print(api.WSSConfiguration(params_wss_2))
    # print(api.getWSSOperationsById(1))
    # print(api.getWSSOperationsById(2))
    # print(api.deleteWSSOperationsById(1))
    # print(api.getWSSOperations())

    bn = [float(DAC.bps)] * DAC.Ncarriers
    En = [float(1)] * DAC.Ncarriers
    params_dac_osc = [{'id': 1, 'dac_out': 1, 'osc_in': 1, 'bn': bn, 'En': En, 'eq': 0},
                      {'id': 2, 'dac_out': 2, 'osc_in': 2, 'bn': bn, 'En': En, 'eq': 0}]
    print(api.DACOSCConfiguration(params_dac_osc))
    print(api.getDACOSCOperationsById(1))
    print(api.getDACOSCOperationsById(2))
    # print(api.deleteDACOSCOperationsById(1))
    print(api.getDACOSCOperations())
