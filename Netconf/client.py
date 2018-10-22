from xml.etree import ElementTree

from netconf.client import NetconfSSHSession

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

host = '127.0.0.1'
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
print(config)
