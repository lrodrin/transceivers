"""This is the NETCONF client module.
"""
from lxml import etree
from netconf.client import NetconfSSHSession

host = '10.1.7.64'
port = 830
username = "root"
password = "netlabN."

session = NetconfSSHSession(host, port, username, password)

operations = ["get", "create", "merge", "delete"]
op = operations[2]

if op == "create":
    print("---CREATE---")
    xml = etree.parse('blueSPACE_DRoF_configuration_create_1.xml')
    config = session.edit_config(method='create', newconf=etree.tostring(xml))
    print(etree.tostring(config))

elif op == "merge":
    print("---MERGE---")
    xml = etree.parse('blueSPACE_DRoF_configuration_merge_1.xml')
    config = session.edit_config(method='merge', newconf=etree.tostring(xml))
    print(etree.tostring(config))

elif op == "delete":
    # edit config delete
    print("---DELETE---")
    config = session.edit_config(method='delete', newconf=None)
    print(config)

elif op == "get":
    print("---GET---")
    config = session.get()
    print(etree.tostring(config))

session.close()
