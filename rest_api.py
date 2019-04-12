"""This is the REST API module.
"""
import json
import logging
import requests

logger = logging.getLogger("REST_API")
logger.addHandler(logging.NullHandler())

headers = {"Content-Type": "application/json"}


class RestApi:
    """
    This is a class for the REST API module.

    :ivar int port_dac_osc: Port of DAC/OSC REST Server
    :ivar int port_wss: Port of WSS REST Server
    """
    port_dac_osc = 5000
    port_wss = 5001

    def __init__(self, ip):
        """
        The constructor for the REST API class.

        :param ip: REST Server ip address
        :type ip: str
        """
        self.ip = ip
        self.port_dac_osc = RestApi.port_dac_osc
        self.port_wss = RestApi.port_wss

    def dacOscConfiguration(self, params):
        """
        DAC and OSC configuration performs DSP to modulate/demodulate an OFDM signal.
        DAC configuration creates an OFDM signal and uploads it to Leia DAC.
        OSC configuration adquires the transmitted OFDM signal and perform DSP to retrieve the original datastream.

        :param params: a transmission
        :type params: list
        :return: estimated SNR per subcarrier and BER
        :rtype: list
        """
        logging.debug('RestApi.dacOscConfiguration')
        url = "http://" + self.ip + ':' + str(self.port_dac_osc) + "/api/dac_osc"
        try:
            response = requests.post(url, headers=headers, data=json.dumps(params))
            data = response.json()
            logging.debug('Response from {}:\n\t{}'.format(url, data))

        except Exception as e:
            logging.error(e)
            raise e

        return data

    def getDACOSCOperations(self):
        """
        DAC and OSC logical associations.
        Get multiple logical associations configured between DAC and OSC.

        :return: logical associations configured between DAC and OSC
        :rtype: dict
        """
        logging.debug('RestApi.getDACOSCOperations')
        url = "http://" + self.ip + ':' + str(self.port_dac_osc) + "/api/dac_osc"
        try:
            response = requests.get(url, headers=headers)
            data = response.json()
            logging.debug('Response from {}:\n\t{}'.format(url, data))

        except Exception as e:
            logging.error(e)
            raise e

        return data

    def getDACOSCOperationsById(self, assoc_id):
        """
        DAC and OSC logical association by ID.
        Returns logical association configured between DAC and OSC specified by id.

        :param assoc_id: id of logical association configured between DAC and OSC
        :type assoc_id: int
        :return: logical association configured between DAC and OSC specified by assoc_id
        :rtype: dict
        """
        logging.debug('RestApi.getDACOSCOperationsById')
        url = "http://" + self.ip + ':' + str(self.port_dac_osc) + "/api/dac_osc/" + str(assoc_id)
        try:
            response = requests.get(url, headers=headers)
            data = response.json()
            logging.debug('Response from {}:\n\t{}'.format(url, data))

        except Exception as e:
            logging.error(e)
            raise e

        return data

    def deleteDACOSCOperationsById(self, assoc_id):
        """
        DAC and OSC logical association by ID.
        Delete logical association configured between DAC and OSC specified by id.

        :param assoc_id: id of logical association configured between DAC and OSC
        :type assoc_id: int
        :return: successful operation and error otherwise
        :rtype: dict
        """
        logging.debug('RestApi.deleteDACOSCOperationsById')
        url = "http://" + self.ip + ':' + str(self.port_dac_osc) + "/api/dac_osc/" + str(assoc_id)
        try:
            response = requests.delete(url, headers=headers)
            data = response.json()
            logging.debug('Response from {}:\n\t{}'.format(url, data))

        except Exception as e:
            logging.error(e)
            raise e

        return data

    def wSSConfiguration(self, params):
        """
        WaveShaper configuration.
        Sets the configuration file, central wavelength, bandwidth and attenuation/phase per port of a WaveShaper.

        :param params: operations to be configured on the WaveShaper
        :type params: dict
        :return: successful operation and error otherwise
        :rtype: dict
        """
        logging.debug('RestApi.wSSConfiguration')
        url = "http://" + self.ip + ':' + str(self.port_wss) + "/api/wss"
        try:
            response = requests.post(url, headers=headers, data=json.dumps(params))
            data = response.json()
            logging.debug('Response from {}:\n\t{}'.format(url, data))

        except Exception as e:
            logging.error(e)
            raise e

        return data

    def getWSSOperations(self):
        """
        WaveShaper operations.
        Get multiple operations configured on the WaveShapers.

        :return: operations configured on the WaveShapers
        :rtype: dict
        """
        logging.debug('RestApi.getWSSOperations')
        url = "http://" + self.ip + ':' + str(self.port_wss) + "/api/wss"
        try:
            response = requests.get(url, headers=headers)
            data = response.json()
            logging.debug('Response from {}:\n\t{}'.format(url, data))

        except Exception as e:
            logging.error(e)
            raise e

        return data

    def getWSSOperationsById(self, wss_id):
        """
        WaveShaper operations by ID.
        Returns operations configured on a WaveShaper specified by id.

        :param wss_id: id of the WaveShaper
        :type wss_id: int
        :return: operations operations configured on a WaveShaper specified by wss_id
        :rtype: dict
        """
        logging.debug('RestApi.getWSSOperationsById')
        url = "http://" + self.ip + ':' + str(self.port_wss) + "/api/wss/" + str(wss_id)
        try:
            response = requests.get(url, headers=headers)
            data = response.json()
            logging.debug('Response from {}:\n\t{}'.format(url, data))

        except Exception as e:
            logging.error(e)
            raise e

        return data

    def deleteWSSOperationsById(self, wss_id):
        """
        WaveShaper operations by ID.
        Delete operations configured on a WaveShaper specified by id.

        :param wss_id: id of the WaveShaper
        :type wss_id: int
        :return: successful operation and error otherwise
        :rtype: dict
        """
        logging.debug('RestApi.deleteWSSOperationsById')
        url = "http://" + self.ip + ':' + str(self.port_wss) + "/api/wss/" + str(wss_id)
        try:
            response = requests.delete(url, headers=headers)
            data = response.json()
            logging.debug('Response from {}:\n\t{}'.format(url, data))

        except Exception as e:
            logging.error(e)
            raise e

        return data
