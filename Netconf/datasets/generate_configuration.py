"""This module generates the datasets in XML.
"""
from xml.dom.minidom import parseString

from lxml import etree
from os import sys, path

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from lib.dac.dac import DAC


def make_DRoF_configuration(n, op, model, namespace, stat, NCF, FEC, eq, bn, En, SNR, BER):
    """
    Creates the XML DRoF configuration for a YANG model specified by model.

    :param n: number that identify the Agent Core
    :type n: int
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
    :param FEC:
    :type FEC: str
    :param eq: equalization
    :type eq: str
    :param bn: bits per symbol
    :type bn: int
    :param En: power per symbol
    :type En: int
    :param SNR:
    :type SNR: int
    :param BER:
    :type BER: float
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
        set_constellation(bn, En, root)
        fec = etree.SubElement(root, 'FEC')
        fec.text = FEC
        equalization = etree.SubElement(root, 'equalization')
        equalization.text = eq
        set_monitoring(SNR, root)
        ber = etree.SubElement(root, 'BER')
        ber.text = str(BER)
        write_file(config, n, op)

    elif op == "replace":
        set_constellation(bn, En, root)

        write_file(config, n, op)

    elif op == "delete":
        pass


def set_constellation(bn, En, root):
    """
    Creates the constellation list inside the XML configuration.

    :param bn: bits per symbol
    :type bn: int
    :param En: power per symbol
    :type En: int
    :param root: parent lxml element of XML configuration
    :type: lxml.Element
    """
    for i in range(1, DAC.Ncarriers + 1):
        constellation = etree.SubElement(root, 'constellation')
        subcarrier_id = etree.SubElement(constellation, 'subcarrier-id')
        subcarrier_id.text = str(i)
        bitsxsymbol = etree.SubElement(constellation, 'bitsxsymbol')
        bitsxsymbol.text = str(bn)
        powerxsymbol = etree.SubElement(constellation, 'powerxsymbol')
        powerxsymbol.text = str(En)


def set_monitoring(SNR, root):
    for i in range(1, DAC.Ncarriers + 1):
        monitor = etree.SubElement(root, 'monitor')
        subcarrier_id = etree.SubElement(monitor, 'subcarrier-id')
        subcarrier_id.text = str(i)
        snr = etree.SubElement(monitor, 'SNR')
        snr.text = str(SNR)


def write_file(config, n, op):
    """
    Write XML configuration to file.

    :param config: configuration file
    :type config: lxml.Element
    :type n: int
    :param op: identify the NETCONF edit-config operation. create or replace.
    :type op: str
    """
    f = open("blueSPACE_DRoF_configuration_{}_{}.xml".format(op, n), "w")
    f.write(parseString(etree.tostring(config)).toprettyxml())


if __name__ == '__main__':
    NCF = 193.4e6
    FEC = "HD-FEC"
    equalization = "MMSE"
    SNR = 1
    BER = 0.0
    make_DRoF_configuration(1, "create", "DRoF-configuration", "urn:blueSPACE-DRoF-configuration", "active", NCF,
                            FEC, equalization, 2, 1, SNR, BER)
    make_DRoF_configuration(2, "create", "DRoF-configuration", "urn:blueSPACE-DRoF-configuration", "active", NCF,
                            FEC, equalization, 1, 0.707, SNR, BER)

    make_DRoF_configuration(1, "replace", "DRoF-configuration", "urn:blueSPACE-DRoF-configuration", None, None,
                            None, None, 1, 0.0707, None, None)
    make_DRoF_configuration(2, "replace", "DRoF-configuration", "urn:blueSPACE-DRoF-configuration", None, None,
                            None, None, 2, 1, None, None)
