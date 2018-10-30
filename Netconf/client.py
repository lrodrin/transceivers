from xml.etree import ElementTree

from lxml import etree
from netconf import util
from netconf.client import NetconfSSHSession

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

host = '10.1.7.64'
port = 830
username = "admin"
password = "admin"

session = NetconfSSHSession(host, port, username, password)
capa = session.capabilities
print(capa)

sid = session.session_id
print(sid)

config = session.get_config()
xmlstr = ElementTree.tostring(config, encoding='utf8', method='xml')
print(xmlstr.decode('utf8'))

data = util.elm("nc:config")
print(etree.tostring(data))

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
'''
print("JI")
config = session.edit_config(newconf=template)
print(etree.tostring(config))

session.close()
