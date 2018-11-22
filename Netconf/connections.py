from bindingC import node_connectivity
# from helpers import *
from pyangbind.lib.serialise import pybindIETFXMLEncoder
from netconf.client import NetconfSSHSession
from lxml import etree

# connexion parameters
host = '10.1.7.64'
port = 830
username = "root"
password = "netlabN."


def createConnection(connectionid, port_in_id, port_out_out, transceiverid):
    print("CREATE CONNECTION")
    c = node_connectivity()
    c.connection.add(connectionid)
    c.connection[connectionid].port_in_id = port_in_id
    c.connection[connectionid].port_out_out = port_out_out
    c.connection[connectionid].transceiver = transceiverid
    return c


# def addConnnection(nc, connectionid, port_in_id, port_out_out, transceiverid):
#
#     if len(nc.connection) == 0:  # empty connections
#         create_connection(nc, connectionid, port_in_id, port_out_out, transceiverid)
#     else:
#         if connectionid not in nc.connection:
#             create_connection(nc, connectionid ,port_in_id, port_out_out, transceiverid)
#
#     return pybindIETFXMLEncoder.serialise(nc)


if __name__ == '__main__':

    # session = NetconfSSHSession(host, port, username, password)
    c = createConnection("5001", "65792", "65536", "1")
    print(pybindIETFXMLEncoder.serialise(c))
    # config = session.edit_config(newconf=connection)
    # xmlstr = etree.tostring(config, encoding='utf8', xml_declaration=True)
    # print(xmlstr)

    x = node_connectivity()

    c2 = createConnection("5002", "65536", "65792", "1")
    print(pybindIETFXMLEncoder.serialise(c2))

    if c2.connection.items()[0][0] not in c.connection:
        print("NOT IN")
        print(pybindIETFXMLEncoder.serialise(c2))

    else:
        print("IN")

        # print(c2.connection.items()[0][0])

    # write_file('node_connectivity.xml', data)
