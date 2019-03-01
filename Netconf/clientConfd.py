from lxml import etree
from netconf.client import NetconfSSHSession

__author__ = "Ricard Vilalta <ricard.vilalta@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

# connexion parameters
host = 'localhost'
port = 2022
username = "admin"
password = "admin"

# connexion to servers
session = NetconfSSHSession(host, port, username, password)

# servers capabilities
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
    <topology xmlns="urn:topology">
        <node operation="merge"> <!-- modify with delete -->
            <node-id>10.1.7.64</node-id>
            <port>
                <port-id>3</port-id>
            </port>
        </node>
    </topology>
</config>
'''
print("---EDIT CONFIG---")
config = session.edit_config(newconf=new_config)
xmlstr = etree.tostring(config, encoding='utf8', xml_declaration=True)
print(xmlstr)

# close connexion
session.close()
