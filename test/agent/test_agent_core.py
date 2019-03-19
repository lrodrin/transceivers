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
    folder = os.path.join(abs_path, "bluespace/config/")
    files = ["blue_bvt1.cfg", "blue_bvt2.cfg"]
    # files = ["blue_bvt1.cfg", "blue_bvt2.cfg", "metro_bvt1.cfg", "metro_bvt2.cfg"]

    print("Testing AGENT CORE")
    for file in files:
        print("Creating AGENT CORE for %s" % file)
        ac = create_Agent(folder, file)
        NCF = 193.4e6
        bn = np.array(np.ones(DAC.Ncarriers) * DAC.bps, dtype=int).tolist()
        En = np.array(np.ones(DAC.Ncarriers)).tolist()
        eq = "MMSE"
        if file.startswith("blue"):
            print("channel laser = %s" % ac.channel_laser)
            print(ac.logical_associations)

            print(ac.setup(NCF, bn, En, eq))
            print(ac.getSNR(bn, En, eq))
            print(ac.setConstellation(bn, En, eq))
            print(ac.disconnect())

        else:
            pass
