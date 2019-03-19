import ast
import logging
import os
from os import sys, path

from six.moves import configparser

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from agent_core import AgentCore

logging.basicConfig(level=logging.DEBUG)


def create_Agent(folder, filename):
    """
    Creates an Agent Core with the parameters specified by file.

    :param folder: directory that contains Agent Core configuration files
    :type folder: str
    :param filename: configuration file
    :type filename: str
    :return: a new Agent Core
    :rtype: AgentCore
    """
    config = configparser.RawConfigParser()
    config.read(folder + filename)
    agent = AgentCore(
        config.get('laser', 'ip'),
        config.get('laser', 'addr'),
        config.get('laser', 'channel'),
        config.get('laser', 'power'),
        None,
        None,
        None,
        None,
        None,
        ast.literal_eval(config.get('dac_osc', 'logical_associations')),
        config.get('rest_api', 'ip')
    )
    return agent


if __name__ == '__main__':
    abs_path = os.path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
    folder = os.path.join(abs_path, "config/")
    files = ["blue_bvt1.cfg", "blue_bvt2.cfg"]
    # files = ["blue_bvt1.cfg", "blue_bvt2.cfg", "metro_bvt1.cfg", "metro_bvt2.cfg"]

    print("Testing AGENT CORE")
    for file in files:
        print("Creating AGENT CORE for %s" % file)
        ac = create_Agent(folder, file)

        if file.startswith("blue"):
            print("channel laser = %s" % ac.channel_laser)
            print(ac.logical_associations)

        else:
            pass
