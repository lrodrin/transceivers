from lxml import etree
from netconf.client import NetconfSSHSession
from pyangbind.lib.serialise import pybindIETFXMLEncoder
from bindingConnection import node_connectivity

__author__ = "Laura Rodriguez Navas <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

# connexion parameters
host = '10.1.7.64'
port = 830
username = "root"
password = "netlabN."


def addConnection(connectionid, port_in_id, port_out_out, transceiverid):
    print("CREATE CONNECTION " + connectionid)
    node_con = node_connectivity()
    node_con.connection.add(connectionid)
    node_con.connection[connectionid].port_in_id = port_in_id
    node_con.connection[connectionid].port_out_out = port_out_out
    node_con.connection[connectionid].transceiver = transceiverid
    return node_con


if __name__ == '__main__':
    session = NetconfSSHSession(host, port, username, password)
    c = addConnection("5001", "65792", "65536", "1")
    c2 = addConnection("5002", "65536", "65792", "1")
    c3 = addConnection("5003", "65536", "65792", "1")
    c4 = addConnection("5004", "65536", "65792", "1")

    opC = 'create'
    opD = 'delete'
    print("--EDIT CONFIG 1--")
    config = session.edit_config(method=opC, newconf=pybindIETFXMLEncoder.serialise(c))
    xmlstr = etree.tostring(config, encoding='utf8', xml_declaration=True)
    print(xmlstr)

    print("--EDIT CONFIG 2--")
    config = session.edit_config(method=opC, newconf=pybindIETFXMLEncoder.serialise(c2))
    xmlstr = etree.tostring(config, encoding='utf8', xml_declaration=True)
    print(xmlstr)

    print("--EDIT CONFIG 3--")
    config = session.edit_config(method=opC, newconf=pybindIETFXMLEncoder.serialise(c3))
    xmlstr = etree.tostring(config, encoding='utf8', xml_declaration=True)
    print(xmlstr)

    print("--EDIT CONFIG 4--")
    nc = node_connectivity()
    nc.connection.add('5002')
    config = session.edit_config(method=opD, newconf=pybindIETFXMLEncoder.serialise(nc))
    xmlstr = etree.tostring(config, encoding='utf8', xml_declaration=True)
    print(xmlstr)

    # print ("NEW CONFIG") new_config = pybindIETFXMLDecoder.decode(pybindIETFXMLEncoder.serialise(c2),
    # capability, 'node-connectivity') new_config = pybindIETFXMLEncoder.serialise(c2) tree_config =
    # etree.XML(new_config) print(etree.tostring(tree_config)) print(etree.tostring(tree_config[0]))

    # print("NODE_CONNECTIVITY")
    # node = pybindIETFXMLEncoder.serialise(c)
    # tree_node = etree.XML(node)
    # print(etree.tostring(tree_node))

    # tree_node.append(tree_config[0])
    # print(etree.tostring(tree_node))

    # write_file('capability.xml', etree.tostring(tree_node))

    # delete
    # tree_node = pybindIETFXMLDecoder.decode(etree.tostring(tree_node), b, 'node-connectivity')
    # deleteConnection(tree_node, '5002')
    # print(pybindIETFXMLEncoder.serialise(tree_node))
