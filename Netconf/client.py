from lxml import etree
from netconf.client import NetconfSSHSession

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

# connexion parameters
host = '10.1.7.64'
port = 830
username = "root"
password = "netlabN."

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
print("---EDIT CONFIG---")
xml = etree.parse('test2.xml')  # new configuration
config = session.edit_config(method='none', newconf=etree.tostring(xml))
xmlstr = etree.tostring(config, encoding='utf8', xml_declaration=True)
print(xmlstr)

# print("---GET---")
# config = session.get_config()
# xmlstr = etree.tostring(config, encoding='utf8', xml_declaration=True)
# print(xmlstr)

session.close()
