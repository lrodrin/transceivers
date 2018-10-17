#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import logging
import os

import json

__author__ = "Laura Rodriguez <laura.rodriguez@cttc.cat>"
__copyright__ = "Copyright 2018, CTTC"

# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('.'.join(os.path.abspath(__name__).split('/')[1:]))


class RyuTopologyApiAccessor:

    def __init__(self,user,password,ip,port,):

        self.user = user
        self.password = password
        self.ip = ip
        self.port = port

    def retrieveTopology(self):
        logger.debug('Retrieving topo from {}:{}'.format(self.ip, self.port))
        http_json = 'http://' + self.ip + ':' + str(self.port) + '/v1.0/topology/links'
        try:
            response = requests.get(http_json, auth=(self.user,
                                    self.password))
            logger.debug('Response from {}:\n\t{}'.format(http_json,response.content))
            topology = json.loads(response.content)
        except Exception as e:
            import sys, traceback
            logger.error({'error': str(sys.exc_info()[0]), 'value': str(sys.exc_info()[1]),
                          'traceback': str(traceback.format_exc()), 'code': 500})
            raise e
        return topology

    def retrieveNodes(self):
        http_json = 'http://' + self.ip + ':' + str(self.port) + '/v1.0/topology/switches'

        response = requests.get(http_json, auth=(self.user,
                                self.password))
        nodes = json.loads(response.content)

        return nodes

    def getNode(self, node_id):
        node_id_int = int(node_id, 16)

        http_json = 'http://' + self.ip + ':' + str(self.port) + '/stats/portdesc/' + str(node_id_int) + ''

        response = requests.get(http_json, auth=(self.user,
                                self.password))
        node = json.loads(response.content)
        return node

    def getPortListFromNode(self, node_id):
        node_id_int = str(int(node_id, 16))
        node_stats = self.getNode(node_id)
        ports = {}
        for (i, node) in enumerate(node_stats[node_id_int]):
            ports[node_stats[node_id_int][i]['name']] = node_stats[node_id_int][i]['port_no']
        return ports

    def dpid_to_ip(self, dpid):
        if dpid=='00003497f65c6de0':
            return '10.1.7.83'
        if dpid == '00003497f65c6ddf':
            return '10.1.7.83'
        return self.change_dpid(dpid)

    # input in format '000000000000'
    # return dpid in format '00:00:00:00:00:00'

    def change_dpid(self, hex_str_dpid):
        common_dpid = ''
        for i in range(0, len(hex_str_dpid)):
            if i != 0 and i % 2 == 0:
                common_dpid += ':'
            common_dpid += hex_str_dpid[i]
        return common_dpid


if __name__ == '__main__':

    print('Testing RYU API')
    API = RyuTopologyApiAccessor('', '', '10.1.7.82', '8080')
    # print(API.change_dpid('0000000000000101'))

    # print(API.retrieveTopology())

    # [{u'src': {u'hw_addr': u'00:1b:21:7a:65:ab', u'name': u'eth5', u'port_no': u'00000002', u'dpid': u'0000000000000101'}, u'dst': {u'hw_addr': u'00:1b:21:7a:69:16', u'name': u'eth5', u'port_no': u'00000001', u'dpid': u'0000000000000102'}}, {u'src': {u'hw_addr': u'00:1b:21:7a:69:16', u'name': u'eth5', u'port_no': u'00000001', u'dpid': u'0000000000000102'}, u'dst': {u'hw_addr': u'00:1b:21:7a:65:ab', u'name': u'eth5', u'port_no': u'00000002', u'dpid': u'0000000000000101'}}]

    # print(API.retrieveNodes())

    # [{u'ports': [{u'hw_addr': u'00:1b:21:7a:65:aa', u'name': u'eth4', u'port_no': u'00000001', u'dpid': u'0000000000000101'}, {u'hw_addr': u'00:1b:21:7a:65:ab', u'name': u'eth5', u'port_no': u'00000002', u'dpid': u'0000000000000101'}], u'dpid': u'0000000000000101'}, {u'ports': [{u'hw_addr': u'00:1b:21:7a:69:16', u'name': u'eth5', u'port_no': u'00000001', u'dpid': u'0000000000000102'}, {u'hw_addr': u'00:1b:21:7a:69:17', u'name': u'eth6', u'port_no': u'00000002', u'dpid': u'0000000000000102'}], u'dpid': u'0000000000000102'}]

    print(API.getNode('000090e2bae2b9c0'))

    # {u'257': [{u'hw_addr': u'00:1b:21:7a:65:aa', u'curr_speed': 10000, u'curr': 8239, u'name': u'eth4', u'supported': 8239, u'state': 0, u'max_speed': 10000, u'advertised': 8239, u'peer': 8239, u'config': 0, u'port_no': 1}, {u'hw_addr': u'00:1b:21:7a:65:ab', u'curr_speed': 10000, u'curr': 8239, u'name': u'eth5', u'supported': 8239, u'state': 0, u'max_speed': 10000, u'advertised': 8239, u'peer': 8239, u'config': 0, u'port_no': 2}]}

    # print(API.getPortListFromNode('0000000000000101'))

    # {u'eth4': 1}
