import bindingC as b
from lxml import etree
from netconf.client import NetconfSSHSession
from pyangbind.lib.serialise import pybindIETFXMLEncoder, pybindIETFXMLDecoder
# from helpers import *

# connexion parameters
host = '10.1.7.64'
port = 830
username = "root"
password = "netlabN."


def addConnection(connectionid, port_in_id, port_out_out, transceiverid):
    print("CREATE CONNECTION " + connectionid)
    nc = b.node_connectivity()
    nc.connection.add(connectionid)
    nc.connection[connectionid].port_in_id = port_in_id
    nc.connection[connectionid].port_out_out = port_out_out
    nc.connection[connectionid].transceiver = transceiverid
    return nc

def deleteConnection(nc, connectionid):
    print("DELETE CONNECTION " + connectionid)
    nc.connection.delete(connectionid)


if __name__ == '__main__':
    session = NetconfSSHSession(host, port, username, password)
    c = addConnection("5001", "65792", "65536", "1")
    c2 = addConnection("5002", "65536", "65792", "1")
    c3 = addConnection("5003", "65536", "65792", "1")

    print("--EDIT CONFIG 1--")
    config = session.edit_config(newconf=pybindIETFXMLEncoder.serialise(c))
    xmlstr = etree.tostring(config, encoding='utf8', xml_declaration=True)
    print(xmlstr)

    print("--EDIT CONFIG 2--")
    config = session.edit_config(newconf=pybindIETFXMLEncoder.serialise(c2))
    xmlstr = etree.tostring(config, encoding='utf8', xml_declaration=True)
    print(xmlstr)

    print("--EDIT CONFIG 3--")
    config = session.edit_config(newconf=pybindIETFXMLEncoder.serialise(c3))
    xmlstr = etree.tostring(config, encoding='utf8', xml_declaration=True)
    print(xmlstr)

    # print ("NEW CONFIG")
    # new_config = pybindIETFXMLDecoder.decode(pybindIETFXMLEncoder.serialise(c2), node_connectivity, 'node-connectivity')
    # new_config = pybindIETFXMLEncoder.serialise(c2)
    # tree_config = etree.XML(new_config)
    # print(etree.tostring(tree_config))
    # print(etree.tostring(tree_config[0]))

    # print("NODE_CONNECTIVITY")
    # node = pybindIETFXMLEncoder.serialise(c)
    # tree_node = etree.XML(node)
    # print(etree.tostring(tree_node))

    # tree_node.append(tree_config[0])
    # print(etree.tostring(tree_node))

    # write_file('node_connectivity.xml', etree.tostring(tree_node))

    # delete
    # tree_node = pybindIETFXMLDecoder.decode(etree.tostring(tree_node), b, 'node-connectivity')
    # deleteConnection(tree_node, '5002')
    # print(pybindIETFXMLEncoder.serialise(tree_node))
