import os
from os import sys, path

from lxml import etree
from netconf import util
from pyangbind.lib import pybindJSON
from pyangbind.lib.serialise import pybindIETFXMLEncoder, pybindIETFXMLDecoder

from Netconf.bindings import bindingConfiguration

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

print(sys.executable)
print(os.getcwd())

XML = etree.parse("blueSPACE_DRoF_configuration_create_1.xml")
new_xml = pybindIETFXMLDecoder.decode(etree.tostring(XML), bindingConfiguration,
                                                      "blueSPACE-DRoF-configuration")

bn = list()
En = list()
for key, value in new_xml.DRoF_configuration.constellation.iteritems():
    bn.append(int(float(value.bitsxsymbol)))
    En.append(float(value.powerxsymbol))

print(bn)
print(En)
print(len(bn))
print(len(En))