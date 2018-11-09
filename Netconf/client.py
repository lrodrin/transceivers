from lxml import etree
from netconf.client import NetconfSSHSession

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

# connexion parameters
host = '10.1.7.64'
port = 830
username = "admin"
password = "admin"

# connexion to server
session = NetconfSSHSession(host, port, username, password)

# server capabilities
c = session.capabilities
print(c)

# get config
print("---GET CONFIG---")
config = session.get_config()
xmlstr = etree.tostring(config, encoding='utf8', xml_declaration=True)
print(xmlstr)

# edit config
new_config = '''
<config>
    <node-topology xmlns="urn:node-topology">
        <node>
            <node-id>10.1.7.64</node-id>
            <port>
                <available-core>
                    <core-id>02</core-id>
                </available-core>
                <port-id>2</port-id>
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
        <node>
            <node-id>10.1.7.67</node-id>
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
print("---EDIT CONFIG---")
config = session.edit_config(newconf=new_config)
xmlstr = etree.tostring(config, encoding='utf8', xml_declaration=True)
print(xmlstr)

# print("---GET---")
# config = session.get()
# xmlstr = etree.tostring(config, encoding='utf8', xml_declaration=True)
# print(xmlstr)

# close connexion
session.close()
