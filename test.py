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

XML = etree.parse("blueSPACE_DRoF_configuration_startup_0.xml")
monitor = XML.findall(".//xmlns:monitor",
                       namespaces={'xmlns': "urn:blueSPACE-DRoF-configuration"})
ber = XML.find(".//xmlns:BER",
                namespaces={'xmlns': "urn:blueSPACE-DRoF-configuration"})

data = util.elm("data")
top = util.subelm(data, "{urn:blueSPACE-DRoF-configuration}blueSPACE-DRoF-configuration")
for value in monitor:
    m = util.subelm(top, 'monitor')
    m.append(util.leaf_elm('subcarrier-id', str(value[0].text)))
    m.append(util.leaf_elm('SNR', str(value[1].text)))

top.append(util.leaf_elm('BER', str(ber.text)))
print(etree.tostring(data))