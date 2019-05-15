"""This is the NETCONF Server module.
"""
import argparse
import ast
import logging
import time
from logging.handlers import RotatingFileHandler
from os import sys, path

import numpy as np
from lxml import etree
from netconf import server, util, nsmap_add, NSMAP
from pyangbind.lib.serialise import pybindIETFXMLEncoder, pybindIETFXMLDecoder
from pyangbind.lib import pybindJSON
from six.moves import configparser

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from agent_core import AgentCore
from bindings import bindingConfiguration

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

nsmap_add("blueSPACE-DRoF-configuration", "urn:blueSPACE-DRoF-configuration")
nsmap_add("blueSPACE-DRoF-TP-capability", "urn:blueSPACE-DRoF-TP-capability")


class NETCONFServer(object):
    """
    This is a class for NETCONF server module.
    """

    def __init__(self, username, password, port, agent):
        """
        The constructor for the NETCONF Server class.

        :param username: username to allow the NETCONF server
        :type username: str
        :param password: password to allow the NETCONF server
        :type password: str
        :param port: port number to bind the NETCONF server
        :type port: int
        :param agent: Agent Core module
        :type agent: AgentCore
        """
        self.ac = agent
        self.capability = None
        self.configuration = bindingConfiguration.blueSPACE_DRoF_configuration()
        self.capabilities = ["blueSPACE-DRoF-configuration", "blueSPACE-DRoF-TP-capability"]
        try:
            auth = server.SSHUserPassController(username=username, password=password)
            self.server = server.NetconfSSHServer(server_ctl=auth, server_methods=self, port=port, debug=False)
            logger.debug("CONNECTION to NETCONF Server on port {} created".format(port))

        except Exception as e:
            logger.error("CONNECTION to NETCONF Server refused, error: {}".format(e))
            raise e

    def close(self):
        """
        Close the NETCONF Server.
        """
        try:
            logger.debug("Connection to NETCONF Server closed")
            self.server.close()

        except Exception as e:
            logger.error("Connection to NETCONF Server not closed, error: {}".format(e))
            raise e

    def load_startup_configuration(self, filename):
        """
        Load startup configuration datastore specified by filename.

        :param filename: configuration file to be loaded
        :type filename: str
        """
        logger.debug("STARTUP CONFIGURATION")
        try:
            XML = open(filename, 'r').read()
            tree = etree.XML(XML)
            data = pybindIETFXMLDecoder.decode(etree.tostring(tree), bindingConfiguration,
                                               "blueSPACE-DRoF-configuration")
            self.configuration = data  # save startup configuration
            logger.info(pybindJSON.dumps(self.configuration))
            logger.debug("STARTUP CONFIGURATION {} loaded".format(filename))

        except Exception as e:
            logger.error("STARTUP CONFIGURATION {} not loaded, error: {}".format(filename, e))
            raise e

    def nc_append_capabilities(self, capabilities):  # pylint: disable=W0613
        """
        Add capabilities.

        :param capabilities: NETCONF server capabilities
        :type capabilities: list
        """
        logger.debug("CAPABILITIES")
        try:
            util.subelm(capabilities, "capability").text = "urn:ietf:params:netconf:capability:xpath:1.0"
            for c in self.capabilities:
                util.subelm(capabilities, "capability").text = NSMAP[c]

            logger.debug("CAPABILITIES {} added".format(self.capabilities))

        except Exception as e:
            logger.error("CAPABILITIES not added, error: {}".format(e))
            raise e

    def rpc_get(self, session, rpc, filter_or_none):  # pylint: disable=W0613
        """
        Retrieve all or part of specified configuration.

        :param session: the server session with the client
        :type session: NetconfServerSession
        :param rpc: the topmost element in the received message
        :type rpc: lxml.Element
        :param filter_or_none: the filter element if present
        :type filter_or_none: lxml.Element or None
        :return: "nc:data" type containing the requested state
        :rtype: lxml.Element
        """
        logger.debug("GET")
        try:
            # extract bn, En and eq from running configuration datastore using pyangbind format
            eq = str(self.configuration.DRoF_configuration.equalization)
            bn, En = self.extract_bn_and_En(self.configuration)

            # DAC/OSC setup
            result = self.ac.dac_setup(bn, En, eq)

            # modify SNR and BER in running configuration datastore
            SNR = result[0]
            BER = result[1]
            self.modify_SNR_and_BER(BER, SNR)
            logger.info(pybindJSON.dumps(self.configuration))

            # get new SNR and BER from running configuration datastore
            data = etree.XML(pybindIETFXMLEncoder.serialise(self.configuration))
            monitor = data.findall(".//xmlns:monitor",
                                   namespaces={'xmlns': "urn:blueSPACE-DRoF-configuration"})
            ber = data.find(".//xmlns:BER",
                            namespaces={'xmlns': "urn:blueSPACE-DRoF-configuration"})

            # create NETCONF rpc-reply message with the new SNR and BER from running configuration datastore
            data_reply = util.elm("data")
            top = util.subelm(data_reply, "{urn:blueSPACE-DRoF-configuration}DRoF-configuration")
            for value in monitor:
                m = util.subelm(top, 'monitor')
                m.append(util.leaf_elm('subcarrier-id', str(value[0].text)))
                m.append(util.leaf_elm('SNR', str(value[1].text)))
            top.append(util.leaf_elm('BER', str(ber.text)))

            return util.filter_results(rpc, data_reply, filter_or_none)

        except Exception as e:
            logger.error("GET, error: {}".format(e))
            raise e

    def modify_SNR_and_BER(self, BER, SNR):
        """
        Modify SNR and BER of running configuration.

        :param BER: bit error rate
        :type BER: float
        :param SNR: SNR per subcarrier
        :type SNR: list
        """
        for i, value in enumerate(self.configuration.DRoF_configuration.monitor.iteritems(), start=1):
            if np.math.isnan(SNR[i - 1]):  # if NAN element
                value[1]._set_SNR(np.format_float_positional(1e-9))
            else:
                value[1]._set_SNR(SNR[i - 1])
        self.configuration.DRoF_configuration._set_BER(BER)

    def rpc_edit_config(self, session, rpc, target, method, newconf):  # pylint disable=W0613
        """
        Create, merge or delete all or part of the specified newconf to the running configuration datastore.

        :param session: the server session with the client
        :type session: NetconfServerSession
        :param rpc: the topmost element in the received message
        :type rpc: lxml.Element
        :param target: the target of the config, defaults to "running"
        :type target: str
        :param method: "merge" (netconf default), "create" or "delete".
        :type method: str
        :param newconf: new configuration
        :type newconf: lxml.Element
        :return: "nc:data" type containing the requested configuration
        :rtype: lxml.Element
        """
        # print(etree.tostring(rpc))
        # print(etree.tostring(method))
        # print(etree.tostring(newconf))
        logger.debug("EDIT CONFIG")
        try:
            if 'capability' in newconf[0].tag:
                # TODO to be implemented
                pass

            elif 'configuration' in newconf[0].tag:
                new_xml = pybindIETFXMLDecoder.decode(etree.tostring(newconf), bindingConfiguration,
                                                      "blueSPACE-DRoF-configuration")
                if "create" in method.text:
                    # extract NCF, bn, En and eq from newconf
                    NCF = float(new_xml.DRoF_configuration.nominal_central_frequency)
                    eq = str(new_xml.DRoF_configuration.equalization)
                    bn, En = self.extract_bn_and_En(new_xml)

                    # Laser setup
                    self.ac.laser_setup(NCF, self.ac.power_laser)

                    # DAC/OSC setup
                    result = self.ac.dac_setup(bn, En, eq)

                    # save newconf as running configuration
                    self.configuration = new_xml

                    # add SNR and BER to running configuration datastore
                    SNR = result[0]
                    BER = result[1]
                    for i in range(1, len(SNR) + 1):
                        m = self.configuration.DRoF_configuration.monitor.add(i)
                        if np.math.isnan(SNR[i - 1]):
                            m._set_SNR(np.format_float_positional(1e-9))
                        else:
                            m._set_SNR(SNR[i - 1])
                    self.configuration.DRoF_configuration._set_BER(BER)

                    logger.info(pybindJSON.dumps(self.configuration))
                    logger.debug("NEW CONFIGURATION created")

                elif "merge" in method.text:
                    # extract bn and En from newconf
                    bn, En = self.extract_bn_and_En(new_xml)

                    # extract eq from running configuration datastore
                    eq = str(self.configuration.DRoF_configuration.equalization)

                    # DAC/OSC setup
                    result = self.ac.dac_setup(bn, En, eq)

                    # modify SNR and BER in running configuration datastore
                    SNR = result[0]
                    BER = result[1]
                    self.modify_SNR_and_BER(BER, SNR)

                    # merge newconf with running configuration datastore
                    for i, x in enumerate(new_xml.DRoF_configuration.constellation.iteritems(), start=1):
                        for j, y in enumerate(self.configuration.DRoF_configuration.constellation.iteritems(), start=1):
                            if i == j:
                                y[1].bitsxsymbol = x[1].bitsxsymbol
                                y[1].powerxsymbol = x[1].powerxsymbol

                    logger.info(pybindJSON.dumps(self.configuration))
                    logger.debug("NEW CONFIGURATION merged")

                elif "delete" in method.text:
                    # disable Laser and remove logical associations between DAC and OSC
                    self.ac.disable_laser()
                    self.ac.remove_logical_associations()

                    # remove the running configuration
                    self.configuration = bindingConfiguration.blueSPACE_DRoF_configuration()

                    logger.info(pybindJSON.dumps(self.configuration))
                    logger.debug("CONFIGURATION deleted")

                return util.filter_results(rpc, etree.XML(pybindIETFXMLEncoder.serialise(self.configuration)), None)

        except Exception as e:
            logger.error("EDIT CONFIG method {}, error: {}".format(method, e))
            raise e

    @staticmethod
    def extract_bn_and_En(configuration):
        """
        Extract bn and En from specified configuration.

        :param configuration: configuration
        :type configuration: bindingConfiguration.blueSPACE_DRoF_configuration()
        :return: bn, En
        :rtype: list, list
        """
        bn = list()
        En = list()
        for key, value in configuration.DRoF_configuration.constellation.iteritems():
            bn.append(int(float(value.bitsxsymbol)))
            En.append(float(value.powerxsymbol))

        return bn, En


def main(*margs):
    parser = argparse.ArgumentParser("NETCONF Server")
    parser.add_argument("-u", default="root", metavar="USERNAME", help='NETCONF Server username')
    parser.add_argument("-pwd", default="netlabN.", metavar="PASSWORD", help='NETCONF Server password')
    parser.add_argument('-p', type=int, default=830, metavar="PORT", help='NETCONF Server connection port')
    parser.add_argument('-c', default="datasets/blueSPACE_DRoF_configuration_startup_0.xml", metavar="STARTUP",
                        help='DRoF Startup Configuration file')
    parser.add_argument('-a', metavar="AGENT CORE", help='BVT Agent Core Configuration file')

    args = parser.parse_args(*margs)
    configure_logger()
    a = init_agent(args.a)
    s = NETCONFServer(args.u, args.pwd, args.p, a)
    s.load_startup_configuration(args.c)

    if sys.stdout.isatty():
        print("^C to quit NETCONF Server")
    try:
        while True:
            time.sleep(1)
    except Exception:
        print("quitting NETCONF Server")

    s.close()


def init_agent(filename):
    """
    Configure Agent Core with configuration file specified by filename.

    :param filename: name of the configuration file needed to configure the Agent Core
    :type filename: str
    :return: Agent Core configured
    :rtype: AgentCore
    """
    try:
        config = configparser.RawConfigParser()
        config.read(filename)
        agent = AgentCore(
            config.get('laser', 'ip'),
            config.get('laser', 'addr'),
            config.get('laser', 'channel'),
            config.get('laser', 'power'),
            None,
            None,
            None,
            None,
            None,
            None,
            ast.literal_eval(config.get('dac_osc', 'logical_associations')),
            config.get('rest_api', 'ip')
        )
        logger.debug("AGENT CORE created with configuration file {}".format(filename))
        return agent

    except Exception as e:
        logger.error("AGENT CORE not created with configuration file {}, error: {}".format(filename, e))
        raise e


def configure_logger():
    """
    Create, formatter and add Handlers (RotatingFileHandler and StreamHandler) to the logger.
    """
    fileHandler = RotatingFileHandler('netconf_server.log', maxBytes=10000000,
                                      backupCount=5)  # File Handler
    streamHandler = logging.StreamHandler()  # Stream Handler
    # Create a Formatter for formatting the logs messages
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(filename)s: %(message)s")
    # Add the Formatter to the Handlers
    fileHandler.setFormatter(formatter)
    streamHandler.setFormatter(formatter)
    # Add Handlers to the logger
    logger.addHandler(fileHandler)
    logger.addHandler(streamHandler)


if __name__ == "__main__":
    main()
