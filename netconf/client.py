from xml.etree import ElementTree

from netconf.client import NetconfSSHSession

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
print(xmlstr)