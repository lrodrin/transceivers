import json
import logging
import requests

logging.basicConfig(level=logging.DEBUG)  # TODO change logging to logger

HEADERS = {"Content-Type": "application/json"}


class RestApiAgentCore:

    def __init__(self, ip, port):
        """
        Initialize the ip address and port number of the Rest Server.

        :param ip: ip address
        :type ip: str
        :param port: port number
        :type port: int
        """
        self.ip = ip
        self.port = port
        self.logical_assoc = None  # TODO per guardar les associacions dac i osc.

    def WSSConfiguration(self, params):
        """
        WaveShaper configuration. This function sets the configuration file, central wavelength, bandwidth and
        attenuation/phase per port to the WaveShaper module.

        :param params: WaveShaper id and a set of operations to configure the WaveShaper
        :type params: dict
        :return:    # TODO
        :rtype: dict
        """
        logging.debug('ResApiAgentCore.WSSConfiguration')
        url = "http://" + self.ip + ':' + str(self.port) + "/api/wss"
        try:
            response = requests.post(url, headers=HEADERS, data=json.dumps(params))
            logging.debug('Response from {}:\n\t{}'.format(url, response.content))
            data = response.content

        except Exception as e:
            logging.error(e)
            raise e

        return data

    def getWSSOperations(self):
        """
        Get operations from a set of WaveShapers.

        :return: # TODO
        :rtype: # TODO
        """
        logging.debug('ResApiAgentCore.getWSSOperations')
        url = "http://" + self.ip + ':' + str(self.port) + "/api/wss"
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
        Get operations from a WaveShaper specified by id.

        :param wss_id: WaveShaper id
        :type wss_id: int
        :return: # TODO
        :rtype: # TODO
        """
        logging.debug('ResApiAgentCore.getWSSOperationsById')
        url = "http://" + self.ip + ':' + str(self.port) + "/api/wss/" + str(wss_id)
        print(url)
        try:
            response = requests.get(url, headers=HEADERS)
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
        :rtype: # TODO
        """
        logging.debug('ResApiAgentCore.deleteWSSOperationsById')
        url = "http://" + self.ip + ':' + str(self.port) + "/api/wss/" + str(wss_id)
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
    params_wss = {'wss_id': 1, 'operation': [
        {'port_in': 1, 'port_out': 1, 'lambda0': 1550.99, 'att': 0.0, 'phase': 0.0, 'bw': 25}]}

    api = RestApiAgentCore('10.1.1.10', 5001)
    print(api.WSSConfiguration(params_wss))
    print(api.getWSSOperations())
    print(api.getWSSOperationsById(1))
    print(api.deleteWSSOperationsById(1))
