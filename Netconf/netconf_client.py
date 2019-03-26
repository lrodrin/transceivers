"""This is the NETCONF client module.
"""
from lxml import etree
from netconf.client import NetconfSSHSession

host = '10.1.7.64'
port = 830
username = "root"
password = "netlabN."

session = NetconfSSHSession(host, port, username, password)

# print("---GET---")
# config = session.get()
# xmlstr = etree.tostring(config, encoding='utf8', xml_declaration=True)
# print(xmlstr)

# edit config
print("---EDIT CONFIG---")
xml = etree.parse('datasets/blueSPACE_DRoF_configuration_create_1.xml')
config = session.edit_config(method='create', newconf=etree.tostring(xml))
print(config)

session.close()


