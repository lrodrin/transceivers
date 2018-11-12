from lxml import etree

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

root_3 = etree.parse('test.xml').getroot()
# root_2 = etree.parse('node1.xml').getroot()
# old = root_1.findall('node')
#
# all_data = []
#
# for o in old:
#     field_dict = {}
#     new = root_2.findall('node')
#
#     for n in new:
#         print(o, n)
#
#     print(field_dict)
#
#     all_data.append(field_dict)
#
# print(all_data)
