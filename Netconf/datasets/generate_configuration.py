"""This module generates the datasets in XML.
"""
from xml.dom.minidom import parseString

from lxml import etree
from os import sys, path

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from lib.dac.dac import DAC


def make_DRoF_configuration(n, op, model, namespace, stat, NCF, FEC, eq, bn, En):
    """
    Creates the XML DRoF configuration for a YANG model specified by model.

    :param n: number that identify the Agent Core
    :type n: str
    :param op: identify the NETCONF edit-config operation. create or replace.
    :type op: str
    :param model: name of the yang model
    :type model: str
    :param namespace: namespace of the yang model
    :type namespace: str
    :param stat: status of DRoF configuration. active, off or standby
    :type stat: str
    :param NCF: nominal central frequency
    :type NCF: float
    :param FEC: # TODO
    :type FEC: str
    :param eq: equalization
    :type eq: str
    :param bn: bits per symbol
    :type bn: list of floats
    :param En: power per symbol
    :type En: list floats
    :return: XML DRoF configuration
    :rtype: lxml.Element
    """
    config = etree.Element('config', xmlns="urn:ietf:params:xml:ns:netconf:base:1.0")
    root = etree.SubElement(config, model, xmlns=namespace)
    if op == "create":
        status = etree.SubElement(root, 'status')
        status.text = stat
        ncf = etree.SubElement(root, 'nominal-central-frequency')
        ncf.text = str(NCF)
        for i in range(1, DAC.Ncarriers + 1):
            constellation = etree.SubElement(root, 'constellation')
            subcarrier_id = etree.SubElement(constellation, 'subcarrier-id')
            subcarrier_id.text = str(i)
            bitsxsymbol = etree.SubElement(constellation, 'bitsxsymbol')
            bitsxsymbol.text = str(bn)
            powerxsymbol = etree.SubElement(constellation, 'powerxsymbol')
            powerxsymbol.text = str(En)
        fec = etree.SubElement(root, 'FEC')
        fec.text = FEC
        equalization = etree.SubElement(root, 'equalization')
        equalization.text = eq

        write_file(config, n, op)

    elif op == "replace":
        for i in range(1, DAC.Ncarriers + 1):
            constellation = etree.SubElement(root, 'constellation')
            subcarrier_id = etree.SubElement(constellation, 'subcarrier-id')
            subcarrier_id.text = str(i)
            bitsxsymbol = etree.SubElement(constellation, 'bitsxsymbol')
            bitsxsymbol.text = str(bn)
            powerxsymbol = etree.SubElement(constellation, 'powerxsymbol')
            powerxsymbol.text = str(En)

        write_file(config, n, op)


def write_file(config, n, op):
    """
    Write XML configuration to file.

    :param config: configuration file
    :type config: lxml.Element
    :type n: str
    :param op: identify the NETCONF edit-config operation. create or replace.
    :type op: str
    """
    f = open("blueSPACE_DRoF_configuration_{}_{}.xml".format(op, n), "w")
    f.write(parseString(etree.tostring(config)).toprettyxml())


if __name__ == '__main__':
    make_DRoF_configuration(1, "create", "DRoF-configuration", "urn:blueSPACE-DRoF-configuration", "active", 193.4e6,
                            "HD-FEC", "MMSE", 2, 1)
    make_DRoF_configuration(2, "create", "DRoF-configuration", "urn:blueSPACE-DRoF-configuration", "active", 193.4e6,
                            "HD-FEC", "MMSE", 1, 0.707)

    make_DRoF_configuration(1, "replace", "DRoF-configuration", "urn:blueSPACE-DRoF-configuration", None, None,
                            None, None, 1, 0.0707)
    make_DRoF_configuration(2, "replace", "DRoF-configuration", "urn:blueSPACE-DRoF-configuration", None, None,
                            None, None, 2, 1)
