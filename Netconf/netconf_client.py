"""This is the NETCONF client module for BVT1 and BVT2 Agents.
"""
import time

from lxml import etree
from netconf.client import NetconfSSHSession

SECS = 30

host_1 = '10.1.7.65'
host_2 = '10.1.7.67'
port = 830
username = "root"
password = "netlabN."
folder = "datasets/"
create_1 = "blueSPACE_DRoF_configuration_create_1.xml"
merge_1 = "blueSPACE_DRoF_configuration_merge_1.xml"
create_2 = "blueSPACE_DRoF_configuration_create_2.xml"
merge_2 = "blueSPACE_DRoF_configuration_merge_2.xml"
delete = "blueSPACE_DRoF_configuration_delete.xml"


def create_config(session, filename):
    print("---CREATE---")
    xml = etree.parse(folder + filename)
    config = session.edit_config(method='create', newconf=etree.tostring(xml).decode('utf-8'))
    return etree.tostring(config).decode('utf-8')


def get_config(session):
    print("---GET---")
    config = session.get()
    return etree.tostring(config).decode('utf-8')


def merge_config(session, filename):
    print("---MERGE---")
    xml = etree.parse(folder + filename)
    config = session.edit_config(method='merge', newconf=etree.tostring(xml).decode('utf-8'))
    return etree.tostring(config).decode('utf-8')


def delete_config(session, filename):
    print("---DELETE---")
    xml = etree.parse(folder + filename)
    config = session.edit_config(method='delete', newconf=etree.tostring(xml).decode('utf-8'))
    return etree.tostring(config).decode('utf-8')


if __name__ == '__main__':
    session_1 = NetconfSSHSession(host_1, port, username, password)
    session_2 = NetconfSSHSession(host_2, port, username, password)
    # create
    print(create_config(session_1, create_1))
    print(create_config(session_2, create_1))
    time.sleep(SECS)
    # get
    print(get_config(session_1))
    print(get_config(session_2))
    time.sleep(SECS)
    # replace
    print(merge_config(session_1, merge_1))
    print(merge_config(session_2, merge_1))
    time.sleep(SECS)
    # delete
    print(delete_config(session_1, delete))
    print(delete_config(session_2, delete))
    session_1.close()
    session_2.close()
