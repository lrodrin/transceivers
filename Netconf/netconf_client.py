"""This is the NETCONF Server module.
"""
from lxml import etree
from netconf.client import NetconfSSHSession

# connexion parameters
host = '10.1.7.64'
port = 830
username = "root"
password = "netlabN."

# connexion to NETCONF Server
session = NetconfSSHSession(host, port, username, password)

# NETCONF Server capabilities
c = session.capabilities
print(c)

# get config operation
print("---GET CONFIG---")
request = session.get_config()
if request:
    response = etree.tostring(request, encoding='utf8', xml_declaration=True)
    print(response)

session.close()
