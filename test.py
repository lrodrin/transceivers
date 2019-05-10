import os
import string
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

och = 'channel-112'
s, n = och.split('-')
print(och.split('-')[1])

client = "c23"
print(client.split('c')[1])
