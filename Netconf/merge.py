from __future__ import print_function

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

from lxml import etree
from netconf import util
template = '''
<config>
<node-topology xmlns="urn:node-topology">
  <node>
    <node-id>10.1.7.64</node-id>
    <port>
      <available-core>
        <core-id>01</core-id>
      </available-core>
      <port-id>2</port-id>
    </port>
  </node>
</node-topology>
</config>
'''.encode("utf-8")

root = etree.XML(template)
# print(root.find("node").tag)

# root = etree.XML("<data><node-topology><node/><node-id/><node/></node-topology></data>")
print(root.find(".//xmlns:node-id", namespaces={'xmlns': 'urn:node-topology'}).text)

for element in root.iter():
    print("%s" % (element.text))
