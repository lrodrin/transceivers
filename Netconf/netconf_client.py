"""This is the NETCONF client module.
"""
import time

from lxml import etree
from netconf.client import NetconfSSHSession

td = 30  # time of execution needed between different netconf operations
ts = 5  # time of execution needed between same netconf operations

host_1 = "10.1.7.65"
host_2 = "10.1.7.67"
port = 830
username = "root"
password = "netlabN."
folder = "datasets/"    # configuration files directory
create_1 = "blueSPACE_DRoF_configuration_create_1.xml"
merge_1 = "blueSPACE_DRoF_configuration_merge_1.xml"
create_2 = "blueSPACE_DRoF_configuration_create_2.xml"
merge_2 = "blueSPACE_DRoF_configuration_merge_2.xml"
delete = "blueSPACE_DRoF_configuration_delete.xml"


def create_config(session, filename):
    """
    The configuration data identified by filename is added to the configuration datastore.

    :param session: NETCONF SSH client session
    :type session: NetconfSSHSession
    :param filename: configuration file
    :type filename: str
    :return: configuration datastore added
    :rtype:
    """
    print("---CREATE---")
    xml = etree.parse(folder + filename)
    config = session.edit_config(method='create', newconf=etree.tostring(xml).decode("utf-8"))
    return etree.tostring(config).decode("utf-8")


def get_config(session):
    """
    Retrieve the configuration and state data.

    :param session: NETCONF SSH client session
    :type session: NetconfSSHSession
    :return: configuration datastore
    :rtype:
    """
    print("---GET---")
    config = session.get()
    return etree.tostring(config).decode("utf-8")


def merge_config(session, filename):
    """
    The configuration data identified by filename is merged with the existing configuration datastore.

    :param session: NETCONF SSH client session
    :type session: NetconfSSHSession
    :param filename: configuration file
    :type filename: str
    :return: configuration datastore merged
    :rtype:
    """
    print("---MERGE---")
    xml = etree.parse(folder + filename)
    config = session.edit_config(method='merge', newconf=etree.tostring(xml).decode("utf-8"))
    return etree.tostring(config).decode("utf-8")


def delete_config(session, filename):
    """
    The configuration data identified by filename is deleted from the existing configuration datastore.

    :param session: NETCONF SSH client session
    :type session: NetconfSSHSession
    :param filename: configuration file
    :type filename: str
    :return: configuration datastore
    :rtype:
    """
    print("---DELETE---")
    xml = etree.parse(folder + filename)
    config = session.edit_config(method='delete', newconf=etree.tostring(xml).decode("utf-8"))
    return etree.tostring(config).decode("utf-8")


if __name__ == '__main__':
    # connection to NETCONF servers
    session_1 = NetconfSSHSession(host_1, port, username, password)
    session_2 = NetconfSSHSession(host_2, port, username, password)

    # create operations
    print(create_config(session_1, create_1))
    time.sleep(ts)
    print(create_config(session_2, create_1))
    time.sleep(td)

    # get operations
    print(get_config(session_1))
    time.sleep(ts)
    print(get_config(session_2))
    time.sleep(td)

    # merge oeprations
    print(merge_config(session_1, merge_1))
    time.sleep(ts)
    print(merge_config(session_2, merge_1))
    time.sleep(td)

    # delete operations
    print(delete_config(session_1, delete))
    time.sleep(ts)
    print(delete_config(session_2, delete))

    session_1.close()
    session_2.close()
