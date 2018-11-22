from bindingC import node_connectivity
from helpers import *
from pyangbind.lib.serialise import pybindIETFXMLEncoder, pybindIETFXMLDecoder
from netconf.client import NetconfSSHSession
from netconf import util
from lxml import etree
import bindingC

# connexion parameters
host = '10.1.7.64'
port = 830
username = "root"
password = "netlabN."


def createConnection(connectionid, port_in_id, port_out_out, transceiverid):
    print("CREATE CONNECTION " + connectionid)
    c = node_connectivity()
    c.connection.add(connectionid)
    c.connection[connectionid].port_in_id = port_in_id
    c.connection[connectionid].port_out_out = port_out_out
    c.connection[connectionid].transceiver = transceiverid
    return c


if __name__ == '__main__':
    session = NetconfSSHSession(host, port, username, password)
    c = createConnection("5001", "65792", "65536", "1")
    c2 = createConnection("5002", "65536", "65792", "1")
    c3 = createConnection("5003", "65536", "65792", "1")

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
    # new_config = pybindIETFXMLDecoder.decode(pybindIETFXMLEncoder.serialise(c2), bindingC, 'node-connectivity')
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

    # c.connection.add(new_config)
    # print(pybindIETFXMLEncoder.serialise(c))
    #
    # t = c.connection.add(c2.connection)
    # print(pybindIETFXMLEncoder.serialise(c))
    #
    # write_file('node_connectivity.xml', etree.tostring(tree_node))
