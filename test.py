import os
from os import sys, path

import numpy as np
from pyangbind.lib import pybindJSON
from lxml import etree
from pyangbind.lib.serialise import pybindIETFXMLDecoder

from Netconf.bindings import bindingConfiguration

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

# print(sys.executable)
# print(os.getcwd())

XML = etree.parse("out_merge.xml")
new_xml = pybindIETFXMLDecoder.decode(etree.tostring(XML), bindingConfiguration,
                                                      "blueSPACE-DRoF-configuration")

for i, value in enumerate(new_xml.DRoF_configuration.monitor.iteritems(), start=1):
    if "nan" in value[1]._get_SNR():
        value[1]._set_SNR(np.format_float_positional(1e-9))
    else:
        value[1]._set_SNR(197.1989696227121)

print(pybindJSON.dumps(new_xml))