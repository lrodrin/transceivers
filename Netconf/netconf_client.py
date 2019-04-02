"""This is the NETCONF client module.
"""
from lxml import etree
from netconf.client import NetconfSSHSession

host = '10.1.7.64'
port = 830
username = "root"
password = "netlabN."

session = NetconfSSHSession(host, port, username, password)

operations = ["create", "get", "merge", "delete"]
op = operations[0]
folder = "datasets/"

if op == "create":
    print("---CREATE---")
    xml = etree.parse(folder + "blueSPACE_DRoF_configuration_create_1.xml")
    config = session.edit_config(method='create', newconf=etree.tostring(xml).decode('utf-8'))
    print(etree.tostring(config).decode('utf-8'))

elif op == "get":
    print("---GET---")
    config = session.get()
    print(etree.tostring(config).decode('utf-8'))

elif op == "merge":
    print("---MERGE---")
    xml = etree.parse(folder + "blueSPACE_DRoF_configuration_merge_1.xml")
    config = session.edit_config(method='merge', newconf=etree.tostring(xml).decode('utf-8'))
    print(etree.tostring(config).decode('utf-8'))

elif op == "delete":
    print("---DELETE---")
    xml = etree.parse(folder + "blueSPACE_DRoF_configuration_delete.xml")
    config = session.edit_config(method='delete', newconf=etree.tostring(xml).decode('utf-8'))
    print(etree.tostring(config).decode('utf-8'))

session.close()
