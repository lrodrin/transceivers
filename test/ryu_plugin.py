import logging
import os
import inspect

from lib.COP.objects_service_topology.ethEdge import EthEdge
from lib.COP.objects_service_topology.node import Node
from lib.COP.objects_service_topology.edgeEnd import EdgeEnd
from lib.COP.objects_service_topology.topology import Topology
from TopologyManager.plugins.RYU_plugin.ryu_api import RyuTopologyApiAccessor


logger = logging.getLogger('.'.join(os.path.abspath(__name__).split('/')[1:]))

class RYU_plugin(object):

    def __init__(self, **kwargs):
        for key in ('ctl_name', 'ctl_addr', 'ctl_port', 'ctl_user',
                    'ctl_password'):
            if key in kwargs:

                # I cut the "ctl_" part of each name.
                setattr(self, key[4:], kwargs[key])

    # print "Intantiating new RYU plugin"

        self.name = 'RYU'
        self.node_type = kwargs['node_type']

    # RYU RESTful API

        self.api = RyuTopologyApiAccessor(self.user, self.password,
                self.addr, self.port)
        self.controller = kwargs['controller']

    def createTopology(self):
        logger.debug(format(inspect.stack()[1]))
        logger.debug('ryuPlugin.createTopology')
        # Topology Manager network representation
        topology = Topology()
        topology_parsed = self.parseTopology(topology)
        return topology_parsed

    def parseTopology(self, topology):
        logger.debug(format(inspect.stack()[1]))
        logger.debug('ryuPlugin.parseTopology')
        logger.debug('Retrieving topology %s',str(self.controller.domainId))
        ryu_topology = self.api.retrieveTransceiver()
        ryu_nodes = self.api.retrieveSlices()
        for ryu_node in ryu_nodes:
            node = Node()
            logger.debug('dpid {}'.format(self.api.change_dpid(ryu_node['dpid'])))
            node.nodeId = self.api.dpid_to_ip(ryu_node['dpid'])
            #ryu_ports = self.api.getPortListFromNode(ryu_node['dpid'])
            for ryu_port in ryu_node['ports']:
                port = EdgeEnd()
                port.edgeEndId = str(int(ryu_port['port_no'], 16))
                port.switchingCap = 'psc'
                port.name = ryu_port['name']
                node.edgeEnd[port.edgeEndId] = port

            node.nodetype.set(self.node_type)
            node.domain = str(self.controller.domainId)
            topology.nodes[node.nodeId] = node


        for edge in ryu_topology:
            e = EthEdge()
            e.source = Node(topology.nodes[self.api.change_dpid(edge['src']['dpid'])].json_serializer()).nodeId
            e.localIfid = str(int(edge['src']['port_no'], 16))
            e.target = Node(topology.nodes[self.api.change_dpid(edge['dst']['dpid'])].json_serializer()).nodeId
            e.remoteIfid = str(int(edge['dst']['port_no'], 16))
            e.edgeId = str(e.source) + '_to_' + str(e.target)
            e.switchingCap = 'psc'
            e.edgeType.set(2)
            e.maxResvBw = '1.0e+9'
            e.unreservBw = '1.0e+9'
            if e.source == '00:00:00:1b:21:7a:69:20' or e.target == '00:00:00:1b:21:7a:69:20' or e.source == '00:00:00:1b:21:7a:65:a8' or e.target == '00:00:00:1b:21:7a:65:a8':
                e.metric = '10'
            else:
                e.metric = '1'

            topology.nodes[e.source].edgeEnd[e.localIfid].peerNodeId = topology.nodes[e.target].nodeId
            topology.nodes[e.source].edgeEnd[e.localIfid].switchingCap = e.switchingCap

            topology.nodes[e.target].edgeEnd[e.remoteIfid].peerNodeId = topology.nodes[e.source].nodeId
            topology.nodes[e.target].edgeEnd[e.remoteIfid].switchingCap = e.switchingCap
            topology.edges[e.edgeId] = e

        #logger.debug('Topology: ' + str(topology))
        return topology

    def refreshTopology(self, topology):
        logger.debug('ryuPlugin.refreshTopology')
        logger.debug(format(inspect.stack()[1]))
        logger.debug('Topology: ' + str(topology))
        topology_parsed = self.parseTopology(topology)
        return topology_parsed

    def __str__(self):
        return self.name


if __name__ == '__main__':
    print 'Testing RYU plugin'

