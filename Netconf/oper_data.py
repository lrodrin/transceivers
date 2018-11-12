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
<data>
    <node-topology>
  <node>
    <node-id>10.1.7.64</node-id>
    <port>
      <port-id>1</port-id>
      <available-core>
        <core-id>1</core-id>
      </available-core>
    </port>
  </node>
  </node-topology>
</data>
'''

data = etree.fromstring(xml.replace(' ', '').replace('\n', ''))
result = util.xpath_filter_result(data, "/devs/dev")
print(etree.tounicode(result))


def nse(xml):
    data = etree.fromstring(xml.replace(' ', '').replace('\n', ''))
    print(etree.tostring(data))
    result = util.xpath_filter_result(data, "//node/*")
    print(etree.tounicode(result))


nse(xml2)
