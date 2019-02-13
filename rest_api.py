import json
import logging

import requests

logging.basicConfig(level=logging.DEBUG)

headers = {"Content-Type": "application/json"}


class ResApiTransceiver:

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def local_assignment(self, params):
        logging.debug("Retrieving local assigment from {}:{}".format(self.ip, self.port))
        url = "http://" + self.ip + ':' + str(self.port) + "/api/vi/openconfig/local_assignment"
        try:
            response = requests.post(url, headers=headers, data=json.dumps(params))
            logging.debug('Response from {}:\n\t{}'.format(url, response.content))
            assignment = response.content

        except Exception as e:  # TODO
            logging.error(e)
            raise e

        return assignment

    def optical_channel_configuration(self, params):
        logging.debug("Retrieving optical_channel_configuration from {}:{}".format(self.ip, self.port))
        url = "http://" + self.ip + ':' + str(self.port) + "/api/vi/openconfig/optical_channel"
        try:

            response = requests.post(url, headers=headers, data=json.dumps(params))
            logging.debug('Response from {}:\n\t{}'.format(url, response.content))
            configuration = response.content

        except Exception as e:
            logging.error(e)
            raise e

        return configuration


if __name__ == '__main__':
    print("Testing REST API")
    api = ResApiTransceiver('10.1.7.64', 5001)
    print(api.local_assignment({'client': 1, 'och': 1}))

    # params = {'och': 1, 'freq': 193.3e6, 'power': -2.97, 'mode': 0}
    # print(api.optical_channel_configuration(params))
