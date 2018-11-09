from lxml import etree

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

tree = etree.XML("<doc><block><title>Text 1</title><content>Stuff I want</content></block><block><title>Text 2</title><content>Stuff I don't want</content></block></doc>")

new_config = '''
<config>
    <node-topology xmlns="urn:node-topology">
        <node>
            <node-id>10.1.7.64</node-id>
            <port>
                <available-core>
                    <core-id>01</core-id>
                </available-core>
                <port-id>1</port-id>
            </port>
        </node>
        <node>
            <node-id>10.1.7.66</node-id>
            <port>
                <available-core>
                    <core-id>02</core-id>
                </available-core>
                <port-id>2</port-id>
            </port>
        </node>
    </node-topology>
</config>
'''

topo_config = '''
<data xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"><node-topology xmlns="urn:node-topology">
  <node>
    <node-id>10.1.7.64</node-id>
    <port>
      <available-core>
        <core-id>1</core-id>
      </available-core>
      <port-id>1</port-id>
    </port>
  </node>
  <node>
    <node-id>10.1.7.65</node-id>
    <port>
      <available-core>
        <core-id>1</core-id>
      </available-core>
      <port-id>1</port-id>
    </port>
  </node>
</node-topology><node-topology:node xmlns:node-topology="urn:node-topology"/></data>
'''
t = etree.XML(topo_config)
d = etree.XML(new_config)
print(tree.xpath('//title/text()'))
print(t.xpath('///node-id/text()'))

print(t.xpath("///xmlns:node-id/text()", namespaces={'xmlns': 'urn:node-topology'}))
print(d.xpath("///xmlns:node-id/text()", namespaces={'xmlns': 'urn:node-topology'}))

print("TESTING OPTIMITZATION :D")
# d = etree.XML(etree.tostring(new_config))
t_list = t.xpath("///xmlns:node-id/text()", namespaces={'xmlns': 'urn:node-topology'})
print(t.xpath("///xmlns:node-id/text()", namespaces={'xmlns': 'urn:node-topology'}))
# print(d.xpath("///xmlns:node-id/text()", namespaces={'xmlns': 'urn:node-topology'}))
data_list = d.findall(".//xmlns:node", namespaces={'xmlns': 'urn:node-topology'})

for data in data_list:
    print(etree.tostring(data))
    for node_id in data.iter("{urn:node-topology}node-id"):
        print("%s - %s" % (node_id.text, t_list))
        if node_id.text in t_list:
            print("MATCH")
        else:
            print("NO MATCH")
            parent = t.find(".//xmlns:node", namespaces={'xmlns': 'urn:node-topology'})
            parent.append(data)
            # t.append(data)

print(etree.tostring(t))