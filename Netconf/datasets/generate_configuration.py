"""This module generates the datasets in XML.
"""
from xml.dom.minidom import parseString

import numpy as np
from lxml import etree


def make_DRoF_configuration(model, namespace, stat, NCF, FEC, eq, sub_id, bn, En):
    """
    Creates the XML DRoF configuration for a YANG model specified by model.

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
    :param sub_id: subcarrier id
    :type sub_id: int
    :param bn: bits per symbol
    :type bn: list of floats
    :param En: power per symbol
    :type En: list floats
    :return: XML DRoF configuration
    :rtype: lxml.Element
    """
    config = etree.Element('config', xmlns="urn:ietf:params:xml:ns:netconf:base:1.0")
    root = etree.SubElement(config, model, xmlns=namespace)
    status = etree.SubElement(root, 'status')
    status.text = stat
    ncf = etree.SubElement(root, 'nominal-central-frequency')
    ncf.text = str(NCF)
    constellation = etree.SubElement(root, 'constellation')
    subcarrier_id = etree.SubElement(constellation, 'subcarrier-id')
    subcarrier_id.text = str(sub_id)
    bitsxsymbol = etree.SubElement(constellation, 'bitsxsymbol')
    bitsxsymbol.text = str(bn)
    powerxsymbol = etree.SubElement(constellation, 'powerxsymbol')
    powerxsymbol.text = str(En)
    fec = etree.SubElement(root, 'FEC')
    fec.text = FEC
    equalization = etree.SubElement(root, 'equalization')
    equalization.text = eq

    return parseString(etree.tostring(config)).toprettyxml()


if __name__ == '__main__':
    bn = np.array(np.ones(512) * 2).tolist()
    En = np.array(np.ones(512)).tolist()
    xml = make_DRoF_configuration("DRoF-configuration", "urn:blueSPACE-DRoF-configuration", "active", 193.4e6,
                                  "HD-FEC", "MMSE", 1, bn, En)
    print(xml)

    filename = "blueSPACE_DRoF_configuration.xml"
    f = open(filename, "w")
    f.write(xml)
