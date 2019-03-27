import collections
import re

from lxml import etree
from pyangbind.lib.serialise import pybindIETFXMLDecoder, pybindIETFXMLEncoder
from netconf import error, server, util

from pyangbind.lib import pybindJSON

from bindings import bindingConfiguration

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"


class XMLCombiner(object):
    def __init__(self, filenames):
        assert len(filenames) > 0, 'No filenames!'
        # save all the roots, in order, to be processed later
        self.roots = [etree.parse(f).getroot() for f in filenames]

    def combine(self):
        for root in self.roots[1:]:
            # combine each element with the first one, and update that
            self.combine_element(self.roots[0], root)
        # return the string representation
        return etree.tostring(self.roots[0])

    def combine_element(self, one, other):
        """
        This function recursively updates either the text or the children
        of an element if another element is found in `one`, or adds it
        from `other` if not found.
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
                    self.combine_element(mapping[el.tag], el)
                except KeyError:
                    # Not in the mapping
                    mapping[el.tag] = el
                    # Just add it
                    one.append(el)


if __name__ == '__main__':
    # r = XMLCombiner(('node1.xml', 'node2.xml')).combine()
    r = XMLCombiner(('blueSPACE_DRoF_configuration_startup_0.xml', 'blueSPACE_DRoF_configuration_create_1.xml')).combine()
    print(r)


xml_1 = etree.parse("blueSPACE_DRoF_configuration_startup_0.xml")
xml_2 = etree.parse("blueSPACE_DRoF_configuration_create_1.xml")
new_xml_1 = pybindIETFXMLDecoder.decode(etree.tostring(xml_1), bindingConfiguration,
                                                              "blueSPACE-DRoF-configuration")
new_xml_2 = pybindIETFXMLDecoder.decode(etree.tostring(xml_2), bindingConfiguration,
                                                              "blueSPACE-DRoF-configuration")

# a = {"cars": 1, "houses": 2, "schools": 3, "stores": 4}
# b = {"Pens": 1, "Pencils": 2, "Paper": 3}
#
# a.update(b)
# NCF = float(new_xml_1.DRoF_configuration.nominal_central_frequency)
# print(dict(new_xml_1.DRoF_configuration))
#
# a = pybindJSON.OrderedDict(new_xml_1)
# b = pybindJSON.OrderedDict(new_xml_2)
# a.update(b)
# mergeDict = collections.OrderedDict(list(a.items()) + list(b.items()))
# print(pybindJSON.dumps(a['DRoF_configuration']))
# print(pybindJSON.dumps(mergeDict['DRoF_configuration']))

data = util.elm("nc:data")
for elem in xml_1.iter("{" + "urn:blueSPACE-DRoF-configuration" + "}monitor"):
    if '}' in elem.tag:
        elem.tag = elem.tag.split('}', 1)[1]  # strip all namespaces
        print(etree.tostring(elem))
        data.append(elem)

holi = xml_1.findall(".//xmlns:BER", namespaces={'xmlns': "urn:blueSPACE-DRoF-configuration"})
print(holi)

root = etree.tostring(data).replace("<nc:data>", "")
print(etree.tostring(data))
print(xml_1)

# for key, value in xml.DRoF_configuration.monitor.iteritems():
#     value._set_SNR(SNR[int(key) - 1])
#
# # decode XML configuration stored from pyangbind format
# self.configuration = etree.XML(pybindIETFXMLEncoder.serialise(xml))
# # parsed_xml = xml.dom.minidom.parseString(
# #     etree.tostring(self.configuration, encoding="utf-8", xml_declaration=True))
# # logging.info(parsed_xml.toprettyxml(indent="", newl=""))


xml_parsed = pybindIETFXMLDecoder.decode(etree.tostring(xml_1), bindingConfiguration,
                                                   "blueSPACE-DRoF-configuration")
bn = list()
En = list()
for k, v in xml_parsed.DRoF_configuration.constellation.iteritems():
    bn.append(int(v.bitsxsymbol))
    En.append(float(v.powerxsymbol))

