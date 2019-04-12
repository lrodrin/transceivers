import ast
import logging
import os
import numpy as np

from six.moves import configparser
from os import sys, path

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from lib.dac.dac import DAC
from agent_core import AgentCore

logging.basicConfig(level=logging.DEBUG)


def create_Agent(fd, fi):
    """
    Creates an Agent Core with the configuration file parameters specified by file.

    :param fd: directory that contains Agent Core configuration files
    :type fd: str
    :param fi: configuration file
    :type fi: str
    :return: a new Agent Core
    :rtype: AgentCore
    """
    config = configparser.RawConfigParser()
    config.read(fd + fi)
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
    folder = os.path.join(abs_path, "bluespace/config/")
    # print(folder)
    files = ["blue_bvt1.cfg"]
    # files = ["blue_bvt1.cfg", "blue_bvt2.cfg"]

    print("Testing AGENT CORE")
    for file in files:
        print("Linked AGENT CORE for %s" % file)
        ac = create_Agent(folder, file)
        if file.startswith("blue"):
            # print(ac.ip_laser)
            # print(ac.addr_laser)
            # print(ac.channel_laser)
            # print(ac.power_laser)
            # print(ac.logical_associations)
            # print(ac.ip_rest_server)

            NCF = 193.4e6
            bn = np.array(np.ones(DAC.Ncarriers) * DAC.bps, dtype=int).tolist()
            En = np.array(np.ones(DAC.Ncarriers)).tolist()
            eq = "MMSE"

            print(ac.setup(NCF, bn, En, eq))
            # ac.laser_setup(NCF)
            # print(ac.dac_setup(bn, En, eq))
            # print(ac.disconnect())

        else:
            pass
