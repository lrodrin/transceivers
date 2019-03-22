"""This is the NETCONF client module.
"""
import numpy as np
import pyangbind.lib.pybindJSON as pybindJSON
from lxml import etree
from netconf.client import NetconfSSHSession
from pyangbind.lib.serialise import pybindIETFXMLDecoder
from Netconf.bindings import bindingConfiguration
from Netconf.bindings.bindingConfiguration import blueSPACE_DRoF_configuration


if __name__ == '__main__':
    hostTX = '10.1.7.64'
    port = 830
    login = 'root'
    password = 'netlabN.'
    files = ["blueSPACE_DRoF_configuration_create_1.xml", "blueSPACE_DRoF_configuration_create_2.xml",
             "blueSPACE_DRoF_configuration_replace_1.xml", "blueSPACE_DRoF_configuration_replace_2.xml"]
    operation = ["create", "replace"]

    xml = etree.parse("datasets/" + files[0]) # reading XML document

    connectionTX = NetconfSSHSession(hostTX, port, login, password)
    config = connectionTX.edit_config(method='create', newconf=etree.tostring(xml))
    xmlstr = etree.tostring(config, encoding='utf8', xml_declaration=True)
    connectionTX.close()
