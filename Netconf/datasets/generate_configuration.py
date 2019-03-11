"""This module generates the dataset
"""
import sys
from xml.dom.minidom import parseString
from lxml import etree


def make_DRoF_configuration(stat, NCF, FEC, eq, subc_id, bps, pps):
    config = etree.Element('config', xmlns="urn:ietf:params:xml:ns:netconf:base:1.0")
    root = etree.SubElement(config, 'DRoF-configuration', xmlns="urn:blueSPACE-DRoF-configuration")
    status = etree.SubElement(root, 'status')
    status.text = stat
    ncf = etree.SubElement(root, 'nominal-central-frequency')
    ncf.text = NCF
    constellation = etree.SubElement(root, 'constellation')
    subcarrier_id = etree.SubElement(constellation, 'subcarrier-id')
    subcarrier_id.text = subc_id
    bitsxsymbol = etree.SubElement(constellation, 'bitsxsymbol')
    bitsxsymbol.text = bps
    powerxsymbol = etree.SubElement(constellation, 'powerxsymbol')
    powerxsymbol.text = pps
    fec = etree.SubElement(root, 'FEC')
    fec.text = FEC
    equalization = etree.SubElement(root, 'equalization')
    equalization.text = eq

    return parseString(etree.tostring(config)).toprettyxml()


def main():
    configuration = make_DRoF_configuration("active", "NCF", "HD-FEC", "MMSE", "1", "2", "3")
    print(configuration)

    f = open("blueSPACE_DRoF_configuration.xml", "w")
    f.write(configuration)


if __name__ == '__main__':
    sys.exit(main())
