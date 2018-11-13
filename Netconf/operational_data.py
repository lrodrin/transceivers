from lxml import etree
from netconf import util

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

xml = '''
<data>
    <devs>
        <dev>
            <name>dev1</name>
            <slots>1</slots>
        </dev>
        <dev>
            <name>dev2</name>
            <slots>2</slots>
        </dev>
        <dev>
            <name>dev3</name>
            <slots>3</slots>
        </dev>
    </devs>
</data>
'''

xml2 = '''
<node>
    <node-id>10.1.7.67</node-id>
    <port>
      <available-core>
        <core-id>02</core-id>
      </available-core>
      <port-id>2</port-id>
    </port>
  </node>
'''

xml3 = '''
<node xmlns="urn:node-topology">
    <node-id>10.1.7.67</node-id>
    <port>
      <available-core>
        <core-id>02</core-id>
      </available-core>
      <port-id>2</port-id>
    </port>
  </node>
'''

data = etree.fromstring(xml.replace(' ', '').replace('\n', ''))
result = util.xpath_filter_result(data, "/devs/dev")
print(etree.tounicode(result))


def nse(xml):
    data = etree.fromstring(xml.replace(' ', '').replace('\n', ''))
    print(etree.tostring(data))
    result = util.xpath_filter_result(data, "node")
    print(etree.tounicode(result))


print("HOLA")
nse(xml2)
