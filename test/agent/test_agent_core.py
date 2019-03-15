import logging
import ast

from six.moves import configparser
from os import sys, path

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from agent_core import AgentCore

logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    folder = "../config/"
    files = ["blue_bvt1.cfg", "blue_bvt2.cfg", "metro_bvt1.cfg", "metro_bvt2.cfg"]
    config = configparser.RawConfigParser()
    config.read(open(folder + files[0]))
    logging.debug("Testing AGENT CORE")

    ac = AgentCore(
        config.get('laser', 'ip'),
        config.get('laser', 'addr'),
        config.get('laser', 'channel'),
        config.get('laser', 'power'),
        config.get('oa', 'ip'),
        config.get('oa', 'addr'),
        config.get('oa', 'mode'),
        config.get('oa', 'power'),
        ast.literal_eval(config.get('wss', 'operations')),
        ast.literal_eval(config.get('dac_osc', 'logical_associations')),
        config.get('rest_api', 'ip')
    )

    print(ac.ip_laser)
    print(ac.ip_amplifier)
    print(ac.wss_operations)
    print(ac.logical_associations)
    print(ac.ip_rest_server)
