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

fbn = open("20190402_bn_ideal.txt", "r", newline=None)
fen = open("20190402_En_ideal.txt", "r", newline=None)

from itertools import zip_longest
i = 1
for x, y in zip_longest(fbn, fen):
    x = x.strip()
    y = y.strip()
    print("{0} {1}\t{2}".format(i, x, y))
    i += 1