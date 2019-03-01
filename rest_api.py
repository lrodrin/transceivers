"""This is the REST API module.
"""
import json
import logging

import requests

logger = logging.getLogger("API")
logger.addHandler(logging.NullHandler())

headers = {"Content-Type": "application/json"}


class RestApi:
    """
    This is a class for the REST API module.
    Interact with WSS and DAC/OSC modules.

    :ivar int port_dac_osc: Port of DAC/OSC REST Server
    :ivar int port_wss: Port of WSS REST Server
    """
    port_dac_osc = 5000
    port_wss = 5001

    def __init__(self, ip):
        """
        The constructor for the REST API class.

        :param ip: ip_rest_server address
        :type ip: str
        """
        self.ip = ip
        self.port_dac_osc = RestApi.port_dac_osc
        self.port_wss = RestApi.port_wss

    def DACOSCConfiguration(self, params):
        """
        DAC and OSC configuration.

        :param params: a transmission
        :type params: list
        :return: # TODO
        :rtype: dict
        """
        logging.debug('RestApi.DACOSCConfiguration')
        url = "http://" + self.ip + ':' + str(self.port_dac_osc) + "/api/dac_osc"
        try:
            response = requests.post(url, headers=headers, data=json.dumps(params))
            logging.debug('Response from {}:\n\t{}'.format(url, response.content))
            data = response.content

        except Exception as e:
            logging.error(e)
            raise e

        return data

    def getDACOSCOperations(self):
        """
        Get all the logical associations between DAC and OSC.

        :return: logical associations between DAC and OSC
        :rtype: dict
        """
        logging.debug('RestApi.getDACOSCOperations')
        url = "http://" + self.ip + ':' + str(self.port_dac_osc) + "/api/dac_osc"
        try:
            response = requests.get(url, headers=headers)
            logging.debug('Response from {}:\n\t{}'.format(url, response.content))
            data = response.content

        except Exception as e:
            logging.error(e)
            raise e

        return data

    def getDACOSCOperationsById(self, assoc_id):
        """
         Get the logical associations between DAC and OSC specified by assoc_id.

        :param assoc_id: logical association id
        :type assoc_id: int
        :return: logical associations between DAC and OSC assoc_id
        :rtype: dict
        """
        logging.debug('RestApi.getDACOSCOperationsById')
        url = "http://" + self.ip + ':' + str(self.port_dac_osc) + "/api/dac_osc/" + str(assoc_id)
        try:
            response = requests.get(url, headers=headers)
            logging.debug('Response from {}:\n\t{}'.format(url, response.content))
            data = response.content

        except Exception as e:
            logging.error(e)
            raise e

        return data

    def deleteDACOSCOperationsById(self, assoc_id):
        """
        Delete the logical associations between DAC and OSC specified by assoc_id.

        :param assoc_id: logical association id
        :type assoc_id: int
        :return: # TODO
        :rtype: dict
        """
        logging.debug('RestApi.deleteDACOSCOperationsById')
        url = "http://" + self.ip + ':' + str(self.port_dac_osc) + "/api/dac_osc/" + str(assoc_id)
        try:
            response = requests.delete(url, headers=headers)
            logging.debug('Response from {}:\n\t{}'.format(url, response.content))
            data = response.content

        except Exception as e:
            logging.error(e)
            raise e

        return data

    def WSSConfiguration(self, params):
        """
        WaveShaper configuration.

        :param params: id to identify the WaveShaper and a set of operations to configure it
        :type params: dict
        :return: # TODO
        :rtype: dict
        """
        logging.debug('RestApi.WSSConfiguration')
        url = "http://" + self.ip + ':' + str(self.port_wss) + "/api/wss"
        try:
            response = requests.post(url, headers=headers, data=json.dumps(params))
            logging.debug('Response from {}:\n\t{}'.format(url, response.content))
            data = response.content

        except Exception as e:
            logging.error(e)
            raise e

        return data

    def getWSSOperations(self):
        """
        Get all the operations from a set of WaveShapers.

        :return: operations configured to WaveShapers
        :rtype: dict
        """
        logging.debug('RestApi.getWSSOperations')
        url = "http://" + self.ip + ':' + str(self.port_wss) + "/api/wss"
        try:
            response = requests.get(url, headers=headers)
            logging.debug('Response from {}:\n\t{}'.format(url, response.content))
            data = response.content

        except Exception as e:
            logging.error(e)
            raise e

        return data

    def getWSSOperationsById(self, wss_id):
        """
        Get the operations from a WaveShaper specified by wss_id.

        :param wss_id: id to identify the WaveShaper
        :type wss_id: int
        :return: operations configured to specific WaveShaper specified by wss_id
        :rtype: dict
        """
        logging.debug('RestApi.getWSSOperationsById')
        url = "http://" + self.ip + ':' + str(self.port_wss) + "/api/wss/" + str(wss_id)
        try:
            response = requests.get(url, headers=headers)
            logging.debug('Response from {}:\n\t{}'.format(url, response.content))
            data = response.content

        except Exception as e:
            logging.error(e)
            raise e

        return data

    def deleteWSSOperationsById(self, wss_id):
        """
        Delete the operations from a WaveShaper specified by wss_id.

        :param wss_id: id to identify the WaveShaper
        :type wss_id: int
        :return: # TODO
        :rtype: dict
        """
        logging.debug('RestApi.deleteWSSOperationsById')
        url = "http://" + self.ip + ':' + str(self.port_wss) + "/api/wss/" + str(wss_id)
        print(url)
        try:
            response = requests.delete(url, headers=headers)
            logging.debug('Response from {}:\n\t{}'.format(url, response.content))
            data = response.content

        except Exception as e:
            logging.error(e)
            raise e

        return data