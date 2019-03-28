from lxml import etree
from pyangbind.lib.serialise import pybindIETFXMLDecoder, pybindIETFXMLEncoder


from pyangbind.lib import pybindJSON
from bindings import bindingConfiguration

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"


def merge(one, other):
    """
    This function recursively updates either the text or the children
    of an node if another node is found in `one`, or adds it
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
                merge(mapping[el.tag], el)

            except KeyError:
                # Not in the mapping
                mapping[el.tag] = el
                # Just add it
                one.append(el)

    return etree.tostring(one)


xml_1 = etree.parse("blueSPACE_DRoF_configuration_create_1.xml")
xml_2 = etree.parse("blueSPACE_DRoF_configuration_merge_2.xml")
xml_3 = etree.parse("blueSPACE_DRoF_configuration_startup_0.xml")

# encode to pyangbind format
new_xml_1 = pybindIETFXMLDecoder.decode(etree.tostring(xml_1), bindingConfiguration,
                                                              "blueSPACE-DRoF-configuration")
new_xml_2 = pybindIETFXMLDecoder.decode(etree.tostring(xml_2), bindingConfiguration,
                                                              "blueSPACE-DRoF-configuration")
new_xml_3 = pybindIETFXMLDecoder.decode(etree.tostring(xml_3), bindingConfiguration,
                                                              "blueSPACE-DRoF-configuration")
# CREATE
# SNR = [1]*512
# BER = 0.0
# for i in range(1, len(SNR) + 1):
#     m = new_xml_1.DRoF_configuration.monitor.add(i)
#     m._set_SNR(SNR[i-1])
# new_xml_1.DRoF_configuration._set_BER(BER)
#
# xml = pybindIETFXMLEncoder.serialise(new_xml_1)
# print(xml)

# MERGE
SNR = [2]*512
BER = 1.0
new_xml_3.DRoF_configuration._set_BER(BER)
for key, value in new_xml_3.DRoF_configuration.monitor.iteritems():
    value._set_SNR(SNR[int(key) - 1])

xml_3 = etree.XML(pybindIETFXMLEncoder.serialise(new_xml_3))

for conste_1 in xml_3.iter("{" + "urn:blueSPACE-DRoF-configuration" + "}constellation"):
    for conste_2 in xml_2.iter("{" + "urn:blueSPACE-DRoF-configuration"  + "}constellation"):
        merge(conste_2, conste_1)

print(etree.tostring(xml_3))

# for conste_2 in xml_2.iter("{" + "urn:blueSPACE-DRoF-configuration"  + "}constellation"):
#     for conste_3 in xml_3.iter("{" + "urn:blueSPACE-DRoF-configuration" + "}constellation"):
#         merge(conste_3, conste_2)
#
# print(etree.tostring(xml_3))
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

# data = util.elm("nc:data")
# for elem in xml_1.iter("{" + "urn:blueSPACE-DRoF-configuration" + "}monitor"):
#     if '}' in elem.tag:
#         elem.tag = elem.tag.split('}', 1)[1]  # strip all namespaces
#         print(etree.tostring(elem))
#         data.append(elem)
#
# holi = xml_1.findall(".//xmlns:BER", namespaces={'xmlns': "urn:blueSPACE-DRoF-configuration"})
# print(holi)
#
# root = etree.tostring(data).replace("<nc:data>", "")
# print(etree.tostring(data))
# print(xml_1)

# for key, value in xml.DRoF_configuration.monitor.iteritems():
#     value._set_SNR(SNR[int(key) - 1])
#
# # decode XML configuration stored from pyangbind format
# self.configuration = etree.XML(pybindIETFXMLEncoder.serialise(xml))
# # parsed_xml = xml.dom.minidom.parseString(
# #     etree.tostring(self.configuration, encoding="utf-8", xml_declaration=True))
# # logging.info(parsed_xml.toprettyxml(indent="", newl=""))


# xml_parsed = pybindIETFXMLDecoder.decode(etree.tostring(xml_1), bindingConfiguration,
#                                                    "blueSPACE-DRoF-configuration")
# bn = list()
# En = list()
# for k, v in xml_parsed.DRoF_configuration.constellation.iteritems():
#     bn.append(int(v.bitsxsymbol))
#     En.append(float(v.powerxsymbol))

