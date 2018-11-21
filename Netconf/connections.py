from bindingC import node_connectivity
# from helpers import *
from pyangbind.lib.serialise import pybindIETFXMLEncoder


def addConnnection(connectionid, port_in_id, port_out_out, transceiverid):
    nc = node_connectivity()
    nc.connection.add(connectionid)
    nc.connection[connectionid].port_in_id = port_in_id
    nc.connection[connectionid].port_out_out = port_out_out
    nc.connection[connectionid].transceiver = transceiverid
    result_xml = pybindIETFXMLEncoder.serialise(nc)
    print(result_xml)


addConnnection("5001", "65792", "65536", "1")
# write_file('node_connectivity.xml', result_xml)
