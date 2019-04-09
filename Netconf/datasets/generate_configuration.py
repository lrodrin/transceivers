"""This module generates the datasets in XML.
"""
from itertools import zip_longest
from xml.dom.minidom import parseString

from lxml import etree
from os import sys, path

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from lib.dac.dac import DAC


def make_DRoF_configuration(n, op, model, namespace, stat, NCF, FEC, eq, fi, fo, SNR, BER):
    """
    Creates the XML DRoF configuration for a YANG model specified by model.

    :param n: number that identify the Agent Core configuration
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
    :param FEC: fordware error correction
    :type FEC: str
    :param eq: equalization
    :type eq: str
    :param fi: filename with the bits per symbol
    :type fi: str
    :param fo: filename with the power per symbol
    :type fo: str
    :param SNR: estimated SNR per subcarrier
    :type SNR: float
    :param BER: bit error rate
    :type BER: float
    :return: XML DRoF configuration
    :rtype: lxml.Element
    """
    config = etree.Element('config', xmlns="urn:ietf:params:xml:ns:netconf:base:1.0")
    root = etree.SubElement(config, model, xmlns=namespace)
    if op == "create":
        fbn = open(fi, "r", newline=None)
        fen = open(fo, "r", newline=None)
        set_config(fen, FEC, NCF, fbn, eq, root, stat)
        fbn.close()
        fen.close()

    elif op == "merge":
        fbn = open(fi, "r", newline=None)
        fen = open(fo, "r", newline=None)
        set_constellation(fbn, fen, root)
        fbn.close()
        fen.close()

    elif op == "startup":
        fbn = open(fi, "r", newline=None)
        fen = open(fo, "r", newline=None)
        set_config(fen, FEC, NCF, fbn, eq, root, stat)
        set_monitoring(SNR, root)
        ber = etree.SubElement(root, 'BER')
        ber.text = str(BER)
        fbn.close()
        fen.close()

    write_file(config, n, op)


def set_config(fen, FEC, NCF, fbn, eq, root, stat):
    """
    Creates the configurable variables inside the XML DRoF configuration.

    :param fen: file with the power per symbol
    :type fen: file
    :param FEC: fordware error correction
    :type FEC: str
    :param NCF: nominal central frequency
    :type NCF: float
    :param fbn: file with the bits per symbol
    :type fbn: file
    :param eq: equalization
    :type eq: str
    :param root: parent lxml element of XML DRoF configuration
    :type root: lxml.Element
    :param stat: status of DRoF configuration. active, off or standby
    :type stat: str
    """
    status = etree.SubElement(root, 'status')
    status.text = stat
    ncf = etree.SubElement(root, 'nominal-central-frequency')
    ncf.text = str(NCF)
    set_constellation(fbn, fen, root)
    fec = etree.SubElement(root, 'FEC')
    fec.text = FEC
    equalization = etree.SubElement(root, 'equalization')
    equalization.text = eq


def set_constellation(fbn, fen, root):
    """
    Creates the constellation list inside the XML DRoF configuration.

    :param fbn: file with the bits per symbol
    :type fbn: file
    :param fen: file with the power per symbol
    :type fen: file
    :param root: parent lxml element of XML DRoF configuration
    :type root: lxml.Element
    """
    i = 1
    for bn, En in zip_longest(fbn, fen):
        constellation = etree.SubElement(root, 'constellation')
        subcarrier_id = etree.SubElement(constellation, 'subcarrier-id')
        subcarrier_id.text = str(i)
        bitsxsymbol = etree.SubElement(constellation, 'bitsxsymbol')
        bitsxsymbol.text = str(bn.strip())
        powerxsymbol = etree.SubElement(constellation, 'powerxsymbol')
        powerxsymbol.text = str(En.strip())
        i += 1


def set_monitoring(SNR, root):
    """
    Creates the monitor list inside the XML DRoF configuration.

    :param SNR: estimated SNR per subcarrier
    :type SNR: float
    :param root: parent lxml element of XML DRoF configuration
    :type root: lxml.Element
    """
    for i in range(1, DAC.Ncarriers + 1):
        monitor = etree.SubElement(root, 'monitor')
        subcarrier_id = etree.SubElement(monitor, 'subcarrier-id')
        subcarrier_id.text = str(i)
        snr = etree.SubElement(monitor, 'SNR')
        snr.text = str(SNR)


def write_file(config, n, op):
    """
    Write XML configuration to a file.

    :param config: XML configuration
    :type config: lxml.Element
    :param n: number that identify the Agent Core configuration
    :type n: int
    :param op: identify the NETCONF edit-config operation. create or replace.
    :type op: str
    """
    f = open("blueSPACE_DRoF_configuration_{}_{}.xml".format(op, n), "w")
    f.write(parseString(etree.tostring(config)).toprettyxml())
    f.close()


if __name__ == '__main__':
    NCF = 193.4e6
    FEC = "HD-FEC"
    equalization = "MMSE"
    SNR = 1
    BER = 0.0
    bn_ideal = "20190402_bn_ideal.txt"
    En_ideal = "20190402_En_ideal.txt"
    bn_dispersio = "20190402_bn_dispersion.txt"
    En_dispersio = "20190402_En_dispersion.txt"
    make_DRoF_configuration(0, "startup", "DRoF-configuration", "urn:blueSPACE-DRoF-configuration", "active", NCF,
                            FEC, equalization, bn_ideal, En_ideal, SNR, BER)
    make_DRoF_configuration(1, "create", "DRoF-configuration", "urn:blueSPACE-DRoF-configuration", "active", NCF,
                            FEC, equalization, bn_ideal, En_ideal, None, None)
    make_DRoF_configuration(2, "create", "DRoF-configuration", "urn:blueSPACE-DRoF-configuration", "active", NCF,
                            FEC, equalization, bn_dispersio, En_dispersio, None, None)


    make_DRoF_configuration(1, "merge", "DRoF-configuration", "urn:blueSPACE-DRoF-configuration", None, None,
                            None, None, bn_dispersio, En_dispersio, None, None)
    make_DRoF_configuration(2, "merge", "DRoF-configuration", "urn:blueSPACE-DRoF-configuration", None, None,
                            None, None, bn_dispersio, En_dispersio, None, None)
