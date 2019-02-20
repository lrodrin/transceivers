import json
import logging
import requests

logging.basicConfig(level=logging.DEBUG)    # TODO change logging to logger

headers = {"Content-Type": "application/json"}


class RestApiAgentCore:

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def wssConfiguration(self, params):
        """

        :param params:
        :return:
        """
        logging.debug('ResApiAgentCore.wssConfiguration')
        url = "http://" + self.ip + ':' + str(self.port) + "/api/wss"
        try:
            response = requests.post(url, headers=headers, data=json.dumps(params))
            logging.debug('Response from {}:\n\t{}'.format(url, response.content))
            data = response.content

        except Exception as e:
            logging.error(e)
            raise e

        return data

    def getWssOperations(self, wss_id):
        logging.debug('ResApiAgentCore.getWssOperations')
        url = "http://" + self.ip + ':' + str(self.port) + "/api/wss/" + str(wss_id)
        print(url)
        try:
            response = requests.get(url, headers=headers)
            logging.debug('Response from {}:\n\t{}'.format(url, response.content))
            data = response.content

        except Exception as e:
            logging.error(e)
            raise e

        return data


if __name__ == '__main__':
    print("Testing REST API")
    api = RestApiAgentCore('10.1.1.10', 5001)
    print(api.getWssOperations(1))
