import inspect
import json
import logging
import os
import sys
import traceback

import xmltodict
from netconf.client import NetconfSSHSession
from lxml import etree

__author__ = "Laura Rodriguez <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

logger = logging.getLogger('.'.join(os.path.abspath(__name__).split('/')[1:]))


def parseConfiguration(configuration):
    # Converts XML configuration to dict
    
    logger.debug(format(inspect.stack()[1]))
    logger.debug('netconfPlugin.parseConfiguration')
    
    configuration_dict = xmltodict.parse(configuration)
    return json.dumps(configuration_dict, indent=4, sort_keys=True)


class NETCONF_API:

    def __init__(self, user, password, ip, port, ):

        self.user = user
        self.password = password
        self.ip = ip
        self.port = port

    def retrieveConfiguration(self):
        # Gets the NETCONF server configuration

        logger.debug(format(inspect.stack()[1]))
        logger.debug('netconfApi.retrieveConfiguration')

        try:
            connection = NetconfSSHSession(self.ip, self.port, self.user, self.password)
            configuration = connection.get_config()
            configuration_json = parseConfiguration(etree.tostring(configuration))

            return configuration_json

        except Exception as e:
            logger.error({'ERROR': str(sys.exc_info()[0]), 'VALUE': str(sys.exc_info()[1]),
                          'TRACEBACK': str(traceback.format_exc()), 'CODE': 500})
            raise e


if __name__ == '__main__':
    api = NETCONF_API('admin', 'admin', '10.1.7.64', 830)
    config = api.retrieveConfiguration()
    print(config)
#    config = api.retrieveConfiguration('<transceiver/>')
#    print(json.loads(config))
