import collections

from lxml import etree
from netconf import util
from pyangbind.lib.serialise import pybindIETFXMLDecoder, pybindIETFXMLEncoder, YangDataSerialiser, pybindJSONEncoder

from pyangbind.lib import pybindJSON
from Netconf.bindings import bindingConfiguration

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"


xml_1 = etree.parse("blueSPACE_DRoF_configuration_create_1.xml")
xml_2 = etree.parse("blueSPACE_DRoF_configuration_merge_1.xml")

# encode to pyangbind format
new_xml_1 = pybindIETFXMLDecoder.decode(etree.tostring(xml_1), bindingConfiguration, "blueSPACE-DRoF-configuration")
new_xml_2 = pybindIETFXMLDecoder.decode(etree.tostring(xml_2), bindingConfiguration, "blueSPACE-DRoF-configuration")

# CREATE
SNR = [1]*512
BER = 0.0
for i in range(1, len(SNR) + 1):
    m = new_xml_1.DRoF_configuration.monitor.add(i)
    m._set_SNR(SNR[i-1])
new_xml_1.DRoF_configuration._set_BER(BER)

result = pybindIETFXMLEncoder.serialise(new_xml_1)
# print(xml)

# GET
new_xml_1 = pybindIETFXMLDecoder.decode(etree.tostring(etree.XML(result)), bindingConfiguration, "blueSPACE-DRoF-configuration")
SNR = [2] * 512
BER = 2.0
for i, value in enumerate(new_xml_1.DRoF_configuration.monitor.iteritems(), start=1):
    value[1]._set_SNR(SNR[i - 1])
new_xml_1.DRoF_configuration._set_BER(BER)

result = etree.XML(pybindIETFXMLEncoder.serialise(new_xml_1))
# print(etree.tostring(result))

data_reply = util.elm("nc:data")
monitor = result.findall(".//xmlns:monitor",
                              namespaces={'xmlns': "urn:blueSPACE-DRoF-configuration"})
for elem in monitor:
    print(elem)
    data_reply.append(elem)

ber = result.find(".//xmlns:BER",
                              namespaces={'xmlns': "urn:blueSPACE-DRoF-configuration"})  # adding BER
data_reply.append(ber)
print(etree.tostring(data_reply))

# MERGE
SNR = [3] * 512
BER = 3.0
for i, value in enumerate(new_xml_1.DRoF_configuration.monitor.iteritems(), start=1):
    value[1]._set_SNR(SNR[i - 1])
new_xml_1.DRoF_configuration._set_BER(BER)

for i, x in enumerate(new_xml_2.DRoF_configuration.constellation.iteritems(), start=1):
    for j, y in enumerate(new_xml_1.DRoF_configuration.constellation.iteritems(), start=1):
        if i == j:
            y[1].bitsxsymbol = x[1].bitsxsymbol
            y[1].powerxsymbol = x[1].powerxsymbol

result = etree.XML(pybindIETFXMLEncoder.serialise(new_xml_1))
print(etree.tostring(result))

# a = collections.OrderedDict(new_xml_1)
# b = collections.OrderedDict(new_xml_2)
# a.update(b)
# print(a)
#
# from dicttoxml import dicttoxml
# xml=dicttoxml(a, root=False, attr_type=False)
# print(xml)
