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

    def load_file(self, filename, binding, module):
        """
        Load and save the capability file into the NETCONF Server datastore.

        :param filename: XML capability file
        :type filename: str
        :param binding: data instance from a YANG data model specified by module_name
        :type binding: PybindBase
        :param module: YANG module
        :type module: str
        """
        logging.debug("STARTUP CONFIG")
        try:
            xml_root = open(filename, 'r').read()
            cap = pybindIETFXMLDecoder.decode(xml_root, binding, module)
            xml = pybindIETFXMLEncoder.serialise(cap)
            tree = etree.XML(xml)
            # print(etree.tostring(tree, encoding='utf8', xml_declaration=True))
            data = util.elm("nc:data")
            data.append(tree)
            logging.info(etree.tostring(data, encoding='utf8', xml_declaration=True))
            self.capability = data  # save capability
            logging.debug("STARTUP CONFIG {} loaded".format(filename))

        except Exception as e:
            logging.error("STARTUP CONFIG {} not loaded, error: {}".format(filename, e))
            raise e

    def nc_append_capabilities(self, capabilities):  # pylint: disable=W0613
        """
        Add capabilities to the NETCONF Server.
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

    def rpc_get_config(self, session, rpc, source_elm, filter_or_none):  # pylint: disable=W0613
        """
        NETCONF Get-config operation.
        Retrieve all or part of specified configuration.

        :param session: the server session with the client
        :type session: NetconfServerSession
        :param rpc: the topmost element in the received message
        :type rpc: lxml.Element
        :param source_elm: the source element indicating where the config should be drawn from
        :type source_elm: lxml.Element
        :param filter_or_none: the filter element if present
        :type filter_or_none: lxml.Element or None
        :return: "nc:data" type containing the requested configuration
        :rtype: lxml.Element
        """
        # print(etree.tostring(rpc))
        # print(etree.tostring(source_elm))
        # print_current_config(self.configuration)
        logging.debug("GET CONFIG")
        try:
            result = self.ac.dac_setup(bn, En, eq)
            logging.debug("SNR = {}".format(result[0]))
            return util.filter_results(rpc, result[0], filter_or_none)

        except Exception as e:
            logging.error("GET CONFIG, error: {}".format(e))
            raise e

    def rpc_edit_config(self, session, rpc, target, method, new_config):  # pylint disable=W0613
        """
        NETCONF edit-config operation.
        Loads all or part of the specified new_config to the NETCONF Server datastore.

        :param session: the server session with the client
        :type session: NetconfServerSession
        :param rpc: the topmost element in the received message
        :type rpc: lxml.Element
        :param target: is the name of the configuration datastore being edited
        :type target: str
        :param method: type of edit-config operation
        :type method: str
        :param new_config: new configuration which must be rooted in the configuration element
        :type new_config: lxml.Element
        :return: "nc:data" type containing the requested configuration
        :rtype: lxml.Element
        """
        # print(etree.tostring(rpc))
        # print(etree.tostring(method))
        # print(etree.tostring(new_config))
        logging.debug("EDIT CONFIG")
        try:
            if 'capability' in new_config[0].tag:
                conf_path = ".//xmlns:blueSPACE-DRoF-TP-capability"
                conf_namespace = "urn:blueSPACE-DRoF-TP-capability"

            elif 'configuration' in new_config[0].tag:
                module_name = "blueSPACE-DRoF-configuration"
                xml_parsed = pybindIETFXMLDecoder.decode(etree.tostring(new_config), bindingConfiguration,
                                                                 module_name)
                if "create" in method.text:
                    status = xml_parsed.DRoF_configuration.status
                    logging.debug("CONFIGURATION: " + status)

                    NCF = float(xml_parsed.DRoF_configuration.nominal_central_frequency)
                    eq = str(xml_parsed.DRoF_configuration.equalization)
                    fec = str(xml_parsed.DRoF_configuration.FEC)
                    bn = list()
                    En = list()
                    for k, v in xml_parsed.DRoF_configuration.constellation.iteritems():
                        bn.append(int(v.bitsxsymbol))
                        En.append(float(v.powerxsymbol))
                    print(NCF, eq, fec, bn, En)
                    self.ac.setup(NCF, bn, En, eq)
                    self.configuration = new_config

                elif "replace" in method.text:
                    status = self.configuration.status
                    logging.debug("CONFIGURATION: " + status)
                    self.ac.dac_setup(bn, En, eq)

                elif "delete" in method.text:
                    status = self.configuration.status
                    logging.debug("CONFIGURATION: " + status)
                    self.ac.disconnect()

            return util.filter_results(rpc, self.configuration, None)

        except Exception as e:
            logging.error("Edit Config, error: {}".format(e))
            raise e


def merge(one, other):
    """
    This function recursively updates either the text or the children of an lxml.Element if another lxml.Element is
    found in one, or adds it from other if not found.

    :param one: one configuration
    :type one: lxml.Element
    :param other: other configuration
    :type other: lxml.Element
    :return: one configuration merged with other configuration
    :rtype: str
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
                merge(mapping[el.tag], el)

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
    parser.add_argument('-c', metavar="CAPABILITY", help='DRoF Capability file')
    parser.add_argument('-a', metavar="AGENT", help='BVT Agent Configuration file')
    parser.add_argument('-y', type=str, default="blueSPACE_DRoF_TP_capability", metavar="YANG MODEL",
                        help='YANG Capability model')

    args = parser.parse_args(*margs)
    a = init_agent(args.a)
    s = NETCONFServer(args.u, args.pwd, args.p, a)
    # s.load_file(args.c, bindingCapability, args.y)

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
        logging.debug("AGENT CORE created with configuration file {}".format(filename))
        return agent

    except Exception as e:
        logging.error("AGENT CORE not created, error: {}".format(e))
        raise e


if __name__ == "__main__":
    main()
