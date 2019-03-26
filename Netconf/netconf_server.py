"""This is the NETCONF Server module.
"""
import argparse
import ast
import logging
import time
import xml.dom.minidom
from os import sys, path

from lxml import etree
from netconf import server, util, nsmap_add, NSMAP
from pyangbind.lib.serialise import pybindIETFXMLEncoder, pybindIETFXMLDecoder
from six.moves import configparser

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from agent_core import AgentCore
from Netconf.bindings import bindingConfiguration
from Netconf.combine import XMLCombiner

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
        self.configuration = None
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

    def load_file(self, filename):
        """
        Load the startup configuration file into the NETCONF Server datastore.

        :param filename: name of XML configuration file
        :type filename: str
        """
        logging.debug("STARTUP CONFIG")
        try:
            xml_root = open(filename, 'r').read()
            tree = etree.XML(xml_root)
            data = util.elm("nc:data")
            data.append(tree)
            self.configuration = data  # save configuration
            parsed_xml = xml.dom.minidom.parseString(
                etree.tostring(self.configuration, encoding="utf-8", xml_declaration=True))
            logging.info(parsed_xml.toprettyxml(indent="", newl=""))
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

        :param session: The server session with the client.
        :type session: `NetconfServerSession`
        :param rpc: The topmost element in the received message.
        :type rpc: `lxml.Element`
        :param filter_or_none: The filter element if present.
        :type filter_or_none: `lxml.Element` or None
        :return: `lxml.Element` of "nc:data" type containing the requested state.
        :raises: `error.RPCServerError` which will be used to construct an XML error response.
        """
        print(etree.tostring(rpc))
        print(etree.tostring(filter_or_none))
        # print(etree.tostring(self.configuration))
        logging.debug("GET")
        module_name = "blueSPACE-DRoF-configuration"
        try:
            # encode XML configuration stored to pyangbind format
            xml = pybindIETFXMLDecoder.decode(etree.tostring(self.configuration), bindingConfiguration,
                                              module_name)

            # extract bn, En, eq from XML configuration stored in pyangbind format
            En, bn, eq = self.extract_variables_from_XML(xml)

            # DAC/OSC setup
            result = self.ac.dac_setup(bn, En, eq)
            # TODO parse result
            logging.debug(result)

            # for testing without setup call
            SNR = bn
            BER = 1.0
            # save new SNR and BER to XML configuration datastore using pyangbind format
            xml.DRoF_configuration._set_BER = BER
            for key, value in xml.DRoF_configuration.monitor.iteritems():
                value._set_SNR(SNR[int(key) - 1])

            # decode XML configuration stored from pyangbind format
            self.configuration = etree.XML(pybindIETFXMLEncoder.serialise(xml))
            # parsed_xml = xml.dom.minidom.parseString(
            #     etree.tostring(self.configuration, encoding="utf-8", xml_declaration=True))
            # logging.info(parsed_xml.toprettyxml(indent="", newl=""))
            return util.filter_results(rpc, self.configuration, filter_or_none)

        except Exception as e:
            logging.error("GET, error: {}".format(e))
            raise e

    def rpc_edit_config(self, unused_session, rpc, target, method, newconf):  # pylint disable=W0613
        """
        NETCONF edit-config operation.
        Loads all or part of the specified new_config to the NETCONF Server datastore.

        :param unused_session: The server session with the client.
        :type unused_session: `NetconfServerSession`
        :param rpc: The topmost element in the received message.
        :type rpc: lxml.Element`
        param target: the target of the config, defaults to "running".
        :type target: str
        :param method: "merge" (netconf default), "create" or "delete".
        :type method: str
        :param newconf: The new configuration.
        :return: "nc:data" type containing the requested configuration.
        :rtype: lxml.Element
        :raises: `error.RPCServerError` which will be used to construct an XML error response.
        """
        # print(etree.tostring(rpc))
        # print(etree.tostring(method))
        # print(etree.tostring(newconf))
        logging.debug("EDIT CONFIG")
        try:
            if 'capability' in newconf[0].tag:
                pass

            elif 'configuration' in newconf[0].tag:
                module_name = "blueSPACE-DRoF-configuration"
                new_xml = pybindIETFXMLDecoder.decode(etree.tostring(newconf), bindingConfiguration,
                                                      module_name)
                if "create" in method.text:
                    # extract bn, En, eq and NCF from new XML configuration in pyangbind format
                    En, bn, eq, NCF = self.extract_variables_from_XML(new_xml)

                    # Laser and DAC/OSC setup
                    # result = self.ac.setup(NCF, bn, En, eq)
                    # logging.debug(result)

                    # save new XML configuration
                    result = XMLCombiner(self.configuration, newconf).combine()
                    print(result)


                elif "replace" in method.text:
                    # extract bn, En, eq from new XML configuration in pyangbind format
                    En, bn, eq = self.extract_variables_from_XML(module_name)

                    # DAC/OSC setup
                    self.ac.dac_setup(bn, En, eq)

                    # TODO fix merge
                    # store new XML configuration constellation changes
                    # for data in newconf.iter("{" + "urn:blueSPACE-DRoF-configuration" + "}constellation"):
                    #     for data_2 in self.configuration.iter(
                    #             "{" + "urn:blueSPACE-DRoF-configuration" + "}constellation"):
                    #         merge(data_2, data)

                elif "delete" in method.text:
                    if self.configuration is not None:
                        # Disable Laser and delete logical associations between DAC and OSC
                        self.ac.disconnect()
                        # Delete XML configuration stored
                        self.configuration = None  # TODO delete massa cutre

            return util.filter_results(rpc, self.configuration, None)

        except Exception as e:
            logging.error("Edit Config, error: {}".format(e))
            raise e

    @staticmethod
    def extract_variables_from_XML(xml_parsed):
        """
        Extract variables bn, En, eq and NCF from an XML specified by xml_parsed.

        :param xml_parsed: XML configuration in pyangbind format
        :type xml_parsed: PybindBase
        :return: bn, En, eq, NCF
        :rtype: list, list, str, str
        """
        NCF = float(xml_parsed.DRoF_configuration.nominal_central_frequency)
        eq = str(xml_parsed.DRoF_configuration.equalization)
        bn = list()
        En = list()
        for k, v in xml_parsed.DRoF_configuration.constellation.iteritems():
            bn.append(int(v.bitsxsymbol))
            En.append(float(v.powerxsymbol))

        return En, bn, eq, NCF


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
    s.load_file(args.c)

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
    Create an Agent Core with specific configuration file specified by filename.

    :param filename: configuration file to configure the Agent Core
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
            ast.literal_eval(config.get('dac_osc', 'logical_associations')),
            config.get('rest_api', 'ip')
        )
        logging.debug("AGENT CORE linked with configuration file {}".format(filename))
        return agent

    except Exception as e:
        logging.error("AGENT CORE not created, error: {}".format(e))
        raise e


if __name__ == "__main__":
    main()
