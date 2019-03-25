"""This is the NETCONF client module.
"""
import numpy as np
import pyangbind.lib.pybindJSON as pybindJSON
from lxml import etree
from netconf.client import NetconfSSHSession
from pyangbind.lib.serialise import pybindIETFXMLDecoder


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


if __name__ == '__main__':
    hostTX = '10.1.7.64'
    port = 830
    login = 'root'
    password = 'netlabN.'
    files = ["blueSPACE_DRoF_configuration_create_1.xml", "blueSPACE_DRoF_configuration_create_2.xml",
             "blueSPACE_DRoF_configuration_replace_1.xml", "blueSPACE_DRoF_configuration_replace_2.xml"]
    operation = ["create", "replace"]

    xml_1 = etree.parse("datasets/" + "blueSPACE_DRoF_configuration_create_1.xml") # reading XML document
    xml_2 = etree.parse("datasets/" + "blueSPACE_DRoF_configuration_replace_1.xml") # reading XML document

    root_1 = etree.parse('constellations_1.xml')
    root_2 = etree.parse('constellations_2.xml')

    print(etree.tostring(xml_1))

    for data in xml_2.iter("{" + "urn:blueSPACE-DRoF-configuration" + "}constellation"):
        for data_2 in xml_1.iter("{" + "urn:blueSPACE-DRoF-configuration" + "}constellation"):
            merge(data_2, data)

    print(etree.tostring(xml_1))
    # result = merge(xml_1_list, xml_2_list)
    # print(result)

