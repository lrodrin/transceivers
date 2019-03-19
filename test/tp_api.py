from __future__ import print_function
import json
import logging
import os
import sys
import traceback

import requests

# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('.'.join(os.path.abspath(__name__).split('/')[1:]))


class Api:

    def __init__(self, user, password, ip, port):

        self.user = user
        self.password = password
        self.ip = ip
        self.port = port

    def retrieveTransceiver(self):
        logger.debug('Retrieving transceiver from {}:{}'.format(self.ip, self.port))
        http_json = 'http://' + self.ip + ':' + str(self.port) + '/api/transceiver'

        try:
            response = requests.get(http_json, auth=(self.user, self.password))
            logger.debug('Response from {}:\n\t{}'.format(http_json,response.content))
            transceiver = json.dumps(json.loads(response.content))

        except Exception as e:
            logger.error({'error': str(sys.exc_info()[0]), 'value': str(sys.exc_info()[1]),
                          'traceback': str(traceback.format_exc()), 'code': 500})
            raise e

        return transceiver

    def retrieveSlices(self):
        logger.debug('Retrieving slices from {}:{}'.format(self.ip, self.port))
        http_json = 'http://' + self.ip + ':' + str(self.port) + '/api/transceiver/slices'

        try:
            response = requests.get(http_json, auth=(self.user, self.password))
            slices = json.dumps(json.loads(response.content))

        except Exception as e:
            logger.error({'error': str(sys.exc_info()[0]), 'value': str(sys.exc_info()[1]),
                          'traceback': str(traceback.format_exc()), 'code': 500})
            raise e
        return slices
    #
    # def getNode(self, node_id):
    #     node_id_int = int(node_id, 16)
    #
    #     http_json = 'http://' + self.ip_flask_server + ':' + str(self.port) + '/stats/portdesc/' + str(node_id_int) + ''
    #
    #     response = requests.get(http_json, auth=(self.user,
    #                             self.password))
    #     node = json.loads(response.content)
    #     return node
    #
    # def getPortListFromNode(self, node_id):
    #     node_id_int = str(int(node_id, 16))
    #     node_stats = self.getNode(node_id)
    #     ports = {}
    #     for (i, node) in enumerate(node_stats[node_id_int]):
    #         ports[node_stats[node_id_int][i]['name']] = node_stats[node_id_int][i]['port_no']
    #     return ports


if __name__ == '__main__':

    print('Testing Transceiver API')
    api = Api('', '', '10.1.16.53', '5000')
    print(api.retrieveTransceiver())
    print(api.retrieveSlices())
