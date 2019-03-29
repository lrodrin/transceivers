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
from pyangbind.lib import pybindJSON
from six.moves import configparser

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from agent_core import AgentCore
from Netconf.bindings import bindingConfiguration

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
        Load the startup configuration into the NETCONF Server datastore.

        :param filename: name of the XML configuration file
        :type filename: str
        """
        logging.debug("STARTUP CONFIG")
        try:
            xml_root = open(filename, 'r').read()
            tree = etree.XML(xml_root)
            data = util.elm("nc:data")
            data.append(tree)
            self.configuration = data  # save startup configuration

            parsed_xml = xml.dom.minidom.parseString(etree.tostring(self.configuration, encoding="utf-8"))
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
            if self.configuration is not None:
                # extract bn, En and eq from running configuration using pyangbind format
                data = pybindIETFXMLDecoder.decode(etree.tostring(self.configuration), bindingConfiguration,
                                                   "blueSPACE-DRoF-configuration")
                eq = str(data.DRoF_configuration.equalization)
                bn = list()
                En = list()
                for k, v in data.DRoF_configuration.constellation.iteritems():
                    bn.append(int(v.bitsxsymbol))
                    En.append(float(v.powerxsymbol))

                # DAC/OSC setup
                # result = self.ac.dac_setup(bn, En, eq)
                # logging.debug(result)

                # modify SNR and BER to running configuration
                SNR = [2] * 512
                BER = 2.0
                for i, value in enumerate(data.DRoF_configuration.monitor.iteritems(), start=1):
                    value[1]._set_SNR(SNR[i - 1])
                data.DRoF_configuration._set_BER(BER)

                # save new running configuration
                self.configuration = etree.XML(pybindIETFXMLEncoder.serialise(data))
                parsed_xml = xml.dom.minidom.parseString(etree.tostring(self.configuration, encoding="utf-8"))
                logging.info(parsed_xml.toprettyxml(indent="", newl=""))

                # create NETCONF message with SNR and BER needed to reply
                data_reply = util.elm("nc:data")
                monitor = self.configuration.findall(".//xmlns:monitor",
                                         namespaces={'xmlns': "urn:blueSPACE-DRoF-configuration"})
                for elem in monitor:
                    data_reply.append(elem) # adding SNR

                ber = self.configuration.find(".//xmlns:BER",
                                  namespaces={'xmlns': "urn:blueSPACE-DRoF-configuration"})  # adding BER
                data_reply.append(ber)
                logging.debug("Created NETCONF message with SNR and BER needed to reply")
                return util.filter_results(rpc, data_reply, filter_or_none)

        except Exception as e:
            logging.error("GET, error: {}".format(e))
            raise e

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
                if "create" in method.text:
                    if self.configuration is None:
                        # extract NCF, bn, En and eq from newconf using pyangbind format
                        new_xml = pybindIETFXMLDecoder.decode(etree.tostring(newconf), bindingConfiguration,
                                                              "blueSPACE-DRoF-configuration")
                        NCF = float(new_xml.DRoF_configuration.nominal_central_frequency)
                        eq = str(new_xml.DRoF_configuration.equalization)
                        bn = list()
                        En = list()
                        for k, v in new_xml.DRoF_configuration.constellation.iteritems():
                            bn.append(int(v.bitsxsymbol))
                            En.append(float(v.powerxsymbol))

                        # Laser and DAC/OSC setup
                        # result = self.ac.setup(NCF, bn, En, eq)
                        # logging.debug(result)

                        # save newconf as running configuration
                        self.configuration = newconf

                        # add SNR and BER to running configuration
                        SNR = [1] * 512
                        BER = 0.0
                        data = pybindIETFXMLDecoder.decode(etree.tostring(self.configuration), bindingConfiguration,
                                                           "blueSPACE-DRoF-configuration")
                        for i in range(1, len(SNR) + 1):
                            m = data.DRoF_configuration.monitor.add(i)
                            m._set_SNR(SNR[i - 1])
                        data.DRoF_configuration._set_BER(BER)

                        # serialise running configuration
                        self.configuration = etree.XML(pybindIETFXMLEncoder.serialise(data))
                        parsed_xml = xml.dom.minidom.parseString(etree.tostring(self.configuration, encoding="utf-8"))
                        logging.info(parsed_xml.toprettyxml(indent="", newl=""))
                        logging.debug("CONFIGURATION created")
                        return util.filter_results(rpc, self.configuration, None)

                elif "merge" in method.text:
                    if self.configuration is not None:
                        # extract bn and En from newconf using pyangbind format
                        new_xml = pybindIETFXMLDecoder.decode(etree.tostring(newconf), bindingConfiguration,
                                                              "blueSPACE-DRoF-configuration")
                        bn = list()
                        En = list()
                        for k, v in new_xml.DRoF_configuration.constellation.iteritems():
                            bn.append(int(v.bitsxsymbol))
                            En.append(float(v.powerxsymbol))

                        # extract eq from running configuration
                        data = pybindIETFXMLDecoder.decode(etree.tostring(self.configuration), bindingConfiguration,
                                                           "blueSPACE-DRoF-configuration")
                        eq = str(data.DRoF_configuration.equalization)

                        # DAC/OSC setup
                        # result = self.ac.dac_setup(bn, En, eq)
                        # logging.debug(result)

                        # modify SNR and BER to running configuration
                        SNR = [3] * 512
                        BER = 3.0
                        for i, value in enumerate(data.DRoF_configuration.monitor.iteritems(), start=1):
                            value[1]._set_SNR(SNR[i - 1])
                        data.DRoF_configuration._set_BER(BER)

                        # merge newconf with running configuration # TODO optimize
                        for i, x in enumerate(new_xml.DRoF_configuration.constellation.iteritems(), start=1):
                            for j, y in enumerate(data.DRoF_configuration.constellation.iteritems(), start=1):
                                if i == j:
                                    y[1].bitsxsymbol = x[1].bitsxsymbol
                                    y[1].powerxsymbol = x[1].powerxsymbol

                        # serialise running configuration
                        self.configuration = etree.XML(pybindIETFXMLEncoder.serialise(data))
                        parsed_xml = xml.dom.minidom.parseString(etree.tostring(self.configuration, encoding="utf-8"))
                        logging.info(parsed_xml.toprettyxml(indent="", newl=""))
                        logging.debug("CONFIGURATION merged")
                        return util.filter_results(rpc, self.configuration, None)

                elif "delete" in method.text:
                    if self.configuration is not None:
                        # disable Laser and remove logical associations between DAC and OSC
                        # self.ac.disconnect()

                        # remove running configuration
                        # TODO remove self.configuration
                        logging.debug("CONFIGURATION deleted")

        except Exception as e:
            logging.error("EDIT CONFIG method {}, error: {}".format(method, e))
            raise e

    def merge(self, one, other):
        """
        This function recursively updates either the constellation or the children
        of an constellation if another constellation is found in `one`, or adds it
        from `other` if not found.

        :param one: list of constellations of one XML configuration
        :type lxml.Element
        :param other: list of constellations of another XML configuration
        :type other: lxml.Element
        """
        # Create a mapping from tag name to element, as that's what we are filtering with
        mapping = {el.tag: el for el in one}
        for el in other:
            if len(el) == 0:
                # Not nested
                try:
                    # Update the text
                    mapping[el.tag].text = el.text

                except KeyError:
                    # An element with this name is not in the mapping
                    mapping[el.tag] = el
                    # Add it
                    one.append(el)
            else:

                try:
                    # Recursively process the element, and update it in the same way
                    self.merge(mapping[el.tag], el)

                except KeyError:
                    # Not in the mapping
                    mapping[el.tag] = el
                    # Just add it
                    one.append(el)

        return etree.tostring(one)


def main(*margs):
    parser = argparse.ArgumentParser("NETCONF Server")
    parser.add_argument("-u", default="root", metavar="USERNAME", help='NETCONF Server username')
    parser.add_argument("-pwd", default="netlabN.", metavar="PASSWORD", help='NETCONF Server password')
    parser.add_argument('-p', type=int, default=830, metavar="PORT", help='NETCONF Server connection port')
    parser.add_argument('-c', default="blueSPACE_DRoF_configuration_startup_0.xml", metavar="CONFIGURATION",
                        help='DRoF Configuration file')
    parser.add_argument('-a', metavar="AGENT", help='BVT Agent Configuration file')

    args = parser.parse_args(*margs)
    a = init_agent(args.a)
    s = NETCONFServer(args.u, args.pwd, args.p, a)
    # s.load_file(args.c)

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
