"""This is the NETCONF Server module.
"""
import argparse
import ast
import logging
import time
from os import sys, path

from lxml import etree
from netconf import server, util, nsmap_add, NSMAP
from pyangbind.lib.serialise import pybindIETFXMLEncoder, pybindIETFXMLDecoder
from pyangbind.lib import pybindJSON
from six.moves import configparser

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from agent_core import AgentCore
from bindings import bindingConfiguration

logging.basicConfig(level=logging.DEBUG)

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
        :param agent: Agent Core
        :type agent: AgentCore
        """
        self.ac = agent
        self.capability = None
        self.configuration = bindingConfiguration.blueSPACE_DRoF_configuration()
        self.capabilities = ["blueSPACE-DRoF-configuration", "blueSPACE-DRoF-TP-capability"]
        try:
            auth = server.SSHUserPassController(username=username, password=password)
            self.server = server.NetconfSSHServer(server_ctl=auth, server_methods=self, port=port, debug=False)
            logging.debug("CONNECTION to NETCONF Server on port {} created".format(port))

        except Exception as e:
            logging.error("CONNECTION to NETCONF Server refused, error: {}".format(e))
            raise e

    def close(self):
        """
        Close the NETCONF Server.
        """
        try:
            logging.debug("Connection to NETCONF Server closed")
            self.server.close()

        except Exception as e:
            logging.error("Connection to NETCONF Server not closed, error: {}".format(e))
            raise e

    def load_startup_configuration(self, filename):
        """
        Load the startup configuration into the NETCONF Server datastore.

        :param filename: name of the XML configuration file
        :type filename: str
        """
        logging.debug("STARTUP CONFIG")
        try:
            XML = open(filename, 'r').read()
            tree = etree.XML(XML)
            data = pybindIETFXMLDecoder.decode(etree.tostring(tree), bindingConfiguration,
                                               "blueSPACE-DRoF-configuration")
            self.configuration = data  # save startup configuration
            logging.info(pybindJSON.dumps(self.configuration))
            logging.debug("STARTUP CONFIG {} loaded".format(filename))

        except Exception as e:
            logging.error("STARTUP CONFIG {} not loaded, error: {}".format(filename, e))
            raise e

    def nc_append_capabilities(self, capabilities):  # pylint: disable=W0613
        """
        Add capabilities to the NETCONF Server.

        :param capabilities:
        :type capabilities:
        """
        logging.debug("CAPABILITIES")
        try:
            util.subelm(capabilities, "capability").text = "urn:ietf:params:netconf:capability:xpath:1.0"
            for c in self.capabilities:
                util.subelm(capabilities, "capability").text = NSMAP[c]

            logging.debug("CAPABILITIES {} added".format(self.capabilities))

        except Exception as e:
            logging.error("CAPABILITIES not added, error: {}".format(e))
            raise e

    def rpc_get(self, session, rpc, filter_or_none):  # pylint: disable=W0613
        """
        NETCONF Get operation.
        Retrieve all or part of specified configuration.

        :param session: the server session with the client
        :type session: NetconfServerSession
        :param rpc: the topmost element in the received message
        :type rpc: lxml.Element
        :param filter_or_none: the filter element if present
        :type filter_or_none: lxml.Element or None
        :return: "nc:data" type containing the requested state
        :raises: error.RPCServerError which will be used to construct an XML error response
        """
        logging.debug("GET")
        try:
            # extract bn, En and eq from running configuration using pyangbind format
            eq = str(self.configuration.DRoF_configuration.equalization)
            self.extract_bn_and_En(self.configuration)

            # DAC/OSC setup
            # result = self.ac.dac_setup(bn, En, eq)
            # logging.debug(result)

            # modify SNR and BER to running configuration
            SNR = [2] * 512
            BER = 2.0
            self.modify_SNR_and_BER(BER, SNR)
            logging.info(pybindJSON.dumps(self.configuration))

            # create NETCONF message with SNR and BER needed to reply
            data = etree.XML(pybindIETFXMLEncoder.serialise(self.configuration))  # TODO create method
            data_reply = util.elm("nc:data")
            monitor = data.findall(".//xmlns:monitor",
                                   namespaces={'xmlns': "urn:blueSPACE-DRoF-configuration"})
            for elem in monitor:
                data_reply.append(elem)  # adding SNR

            ber = data.find(".//xmlns:BER",
                            namespaces={'xmlns': "urn:blueSPACE-DRoF-configuration"})  # adding BER
            data_reply.append(ber)
            logging.debug("Created NETCONF message with SNR and BER needed to reply")
            return util.filter_results(rpc, data_reply, filter_or_none)

        except Exception as e:
            logging.error("GET, error: {}".format(e))
            raise e

    def modify_SNR_and_BER(self, BER, SNR):
        """
        Modify SNR and BER to running configuration.

        :param BER:
        :type BER: float
        :param SNR:
        :type SNR: list
        """
        for i, value in enumerate(self.configuration.DRoF_configuration.monitor.iteritems(), start=1):
            value[1]._set_SNR(SNR[i - 1])

        self.configuration.DRoF_configuration._set_BER(BER)

    def rpc_edit_config(self, unused_session, rpc, target, method, newconf):  # pylint disable=W0613
        """
        NETCONF edit-config operation.
        Loads all or part of the specified newconf to the NETCONF running configuration.

        :param unused_session: the server session with the client
        :type unused_session: NetconfServerSession
        :param rpc: the topmost element in the received message
        :type rpc: lxml.Element
        param target: the target of the config, defaults to "running"
        :type target: str
        :param method: "merge" (netconf default), "create" or "delete".
        :type method: str
        :param newconf: the new configuration
        :type newconf: lxml.Element
        :return: "nc:data" type containing the requested configuration
        :rtype: lxml.Element
        :raises: `error.RPCServerError` which will be used to construct an XML error response
        """
        # print(etree.tostring(rpc))
        # print(etree.tostring(method))
        # print(etree.tostring(newconf))
        logging.debug("EDIT CONFIG")
        try:
            if 'capability' in newconf[0].tag:
                pass

            elif 'configuration' in newconf[0].tag:
                new_xml = pybindIETFXMLDecoder.decode(etree.tostring(newconf), bindingConfiguration,
                                                      "blueSPACE-DRoF-configuration")
                if "create" in method.text:
                    # extract NCF, bn, En and eq from newconf using pyangbind format
                    NCF = float(new_xml.DRoF_configuration.nominal_central_frequency)
                    eq = str(new_xml.DRoF_configuration.equalization)
                    self.extract_bn_and_En(new_xml)

                    # Laser and DAC/OSC setup
                    # result = self.ac.setup(NCF, bn, En, eq)
                    # logging.debug(result)

                    # save newconf as running configuration
                    self.configuration = new_xml

                    # add SNR and BER to running configuration  # TODO extract method
                    SNR = [1] * 512
                    BER = 0.0
                    for i in range(1, len(SNR) + 1):
                        self.configuration.DRoF_configuration.monitor.add(i)
                        self.configuration.DRoF_configuration.monitor._set_SNR(SNR[i - 1])

                    self.configuration.DRoF_configuration._set_BER(BER)
                    logging.info(pybindJSON.dumps(self.configuration))
                    logging.debug("CONFIGURATION created")

                elif "merge" in method.text:
                    # extract bn and En from newconf using pyangbind format
                    self.extract_bn_and_En(new_xml)

                    # extract eq from running configuration
                    eq = str(self.configuration.DRoF_configuration.equalization)

                    # DAC/OSC setup
                    # result = self.ac.dac_setup(bn, En, eq)
                    # logging.debug(result)

                    # modify SNR and BER to running configuration
                    SNR = [3] * 512
                    BER = 3.0
                    self.modify_SNR_and_BER(BER, SNR)

                    # merge newconf with running configuration # TODO optimize and extract method
                    for i, x in enumerate(new_xml.DRoF_configuration.constellation.iteritems(), start=1):
                        for j, y in enumerate(self.configuration.DRoF_configuration.constellation.iteritems(), start=1):
                            if i == j:
                                y[1].bitsxsymbol = x[1].bitsxsymbol
                                y[1].powerxsymbol = x[1].powerxsymbol

                    logging.info(pybindJSON.dumps(self.configuration))
                    logging.debug("CONFIGURATION merged")

                elif "delete" in method.text:
                    # disable Laser and remove logical associations between DAC and OSC
                    # self.ac.disconnect()

                    self.configuration = bindingConfiguration.blueSPACE_DRoF_configuration()
                    logging.info(pybindJSON.dumps(self.configuration))
                    logging.debug("CONFIGURATION deleted")

                return util.filter_results(rpc, etree.XML(pybindIETFXMLEncoder.serialise(self.configuration)), None)

        except Exception as e:
            logging.error("EDIT CONFIG method {}, error: {}".format(method, e))
            raise e

    @staticmethod
    def extract_bn_and_En(configuration):
        """
        Extract bn and En from configuration.

        :param configuration:
        :type configuration:
        """
        bn = list()
        En = list()
        for k, v in configuration.DRoF_configuration.constellation.iteritems():
            bn.append(int(v.bitsxsymbol))
            En.append(float(v.powerxsymbol))


def main(*margs):
    parser = argparse.ArgumentParser("NETCONF Server")
    parser.add_argument("-u", default="root", metavar="USERNAME", help='NETCONF Server username')
    parser.add_argument("-pwd", default="netlabN.", metavar="PASSWORD", help='NETCONF Server password')
    parser.add_argument('-p', type=int, default=830, metavar="PORT", help='NETCONF Server connection port')
    parser.add_argument('-c', default="datasets/blueSPACE_DRoF_configuration_startup_0.xml", metavar="CONFIGURATION",
                        help='DRoF Configuration file')
    parser.add_argument('-a', metavar="AGENT", help='BVT Agent Configuration file')

    args = parser.parse_args(*margs)
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
    Create an Agent with specific configuration file.

    :param filename: name of configuration file to configure the Agent
    :type filename: str
    :return: Agent configured
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
            ast.literal_eval(config.get('dac_osc', 'logical_associations')),
            config.get('rest_api', 'ip')
        )
        logging.debug("AGENT CORE linked with configuration {}".format(filename))
        return agent

    except Exception as e:
        logging.error("AGENT CORE not linked, error: {}".format(e))
        raise e


if __name__ == "__main__":
    main()
